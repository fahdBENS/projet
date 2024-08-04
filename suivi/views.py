# suivi/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from .models import Lot, Processus, LotProcessus, Message
from .forms import LotForm, ProcessForm, UploadFileForm, ReclamationForm
import pandas as pd
from .decorators import superviseur_required  # Importez votre décorateur personnalisé

def index(request):
    if not request.user.groups.filter(name='Superviseur').exists():
        return redirect('login')  # Redirige vers la page de connexion si l'utilisateur n'est pas un superviseur

    lots = Lot.objects.all()
    processus = Processus.objects.all()
    data = []

    if request.method == 'POST':
        form = ProcessForm(request.POST)
        if form.is_valid():
            lot = form.cleaned_data['lot']
            processus = form.cleaned_data['processus']
            if 'start' in request.POST:
                LotProcessus.objects.update_or_create(
                    lot=lot, processus=processus,
                    defaults={'temps_debut': timezone.now()}
                )
            elif 'end' in request.POST:
                LotProcessus.objects.update_or_create(
                    lot=lot, processus=processus,
                    defaults={'temps_fin': timezone.now()}
                )
            return redirect('index')
    else:
        form = ProcessForm()

    for lot in lots:
        processus_data = []
        for proc in processus:
            lot_proc = LotProcessus.objects.filter(lot=lot, processus=proc).first()
            debut = lot_proc.temps_debut if lot_proc else None
            fin = lot_proc.temps_fin if lot_proc else None
            temps_pris = None
            if debut and fin:
                delta = fin - debut
                temps_pris = int(delta.total_seconds() // 60)
            processus_data.append({
                'processus': proc,
                'debut': debut,
                'fin': fin,
                'temps_pris': temps_pris
            })
        data.append({
            'lot': lot,
            'processus': processus_data
        })

    return render(request, 'index.html', {
        'data': data,
        'form': form
    })

@login_required
@superviseur_required
def add_lot(request):
    if request.method == 'POST':
        form = LotForm(request.POST)
        if form.is_valid():
            new_lot = form.save()
            try:
                planning_input_processus = Processus.objects.get(nom_proc='Planning input')
            except Processus.DoesNotExist:
                messages.error(request, 'Le processus "Planning input" n\'existe pas dans la base de données.')
                return redirect('add_lot')

            current_time = timezone.now()
            LotProcessus.objects.create(
                lot=new_lot,
                processus=planning_input_processus,
                temps_debut=current_time,
                temps_fin=current_time
            )
            messages.success(request, 'Le lot a été ajouté avec succès.')
            return redirect('index')
    else:
        form = LotForm()
    return render(request, 'add_lot.html', {'form': form})

@login_required
@superviseur_required
def upload_lots(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            try:
                df = pd.read_excel(file)
            except Exception as e:
                messages.error(request, f'Erreur lors de la lecture du fichier : {str(e)}')
                return redirect('upload_lots')
            
            try:
                planning_input_processus = Processus.objects.get(nom_proc='Planning input')
            except Processus.DoesNotExist:
                messages.error(request, 'Le processus "Planning input" n\'existe pas dans la base de données.')
                return redirect('upload_lots')

            current_time = timezone.now()
            success_count = 0
            failure_count = 0
            for _, row in df.iterrows():
                ref = row.get('ref')
                quantite = row.get('quantite')
                if ref and quantite:
                    try:
                        lot, created = Lot.objects.update_or_create(
                            ref=ref,
                            defaults={'quantite': quantite}
                        )
                        if created:
                            LotProcessus.objects.create(
                                lot=lot,
                                processus=planning_input_processus,
                                temps_debut=current_time,
                                temps_fin=current_time
                            )
                        success_count += 1
                    except Exception as e:
                        messages.error(request, f'Erreur lors de l\'importation de la référence {ref}: {str(e)}')
                        failure_count += 1

            if success_count > 0:
                messages.success(request, f'Les lots ont été importés avec succès. ({success_count} ajoutés)')
            if failure_count > 0:
                messages.error(request, f'Certaines erreurs se sont produites lors de l\'importation. ({failure_count} erreurs)')

            return redirect('index')
        else:
            messages.error(request, 'Aucun fichier n\'a été téléchargé.')

    return render(request, 'upload_lots.html')

def start_process(request, lot_ref, processus_id):
    if request.method == 'POST':
        lot = get_object_or_404(Lot, ref=lot_ref)
        processus = get_object_or_404(Processus, id=processus_id)
        LotProcessus.objects.update_or_create(
            lot=lot, processus=processus,
            defaults={'temps_debut': timezone.now()}
        )
        return redirect('index')
    return HttpResponseForbidden()

def end_process(request, lot_ref, processus_id):
    if request.method == 'POST':
        lot = get_object_or_404(Lot, ref=lot_ref)
        processus = get_object_or_404(Processus, id=processus_id)
        LotProcessus.objects.update_or_create(
            lot=lot, processus=processus,
            defaults={'temps_fin': timezone.now()}
        )
        return redirect('index')
    return HttpResponseForbidden()
@login_required
def reclamer_lot(request):
    if request.method == 'POST':
        form = ReclamationForm(request.POST)
        if form.is_valid():
            lot = form.cleaned_data['lot']
            processus = form.cleaned_data['processus']
            le_message = form.cleaned_data['le_message']
            responsable = form.cleaned_data['responsable']
            Message.objects.create(
                lot=lot,
                processus=processus,
                temps_reclamation=timezone.now(),
                le_message=le_message,
                responsable=responsable
            )
            messages.success(request, 'La réclamation a été enregistrée avec succès.')
            if not request.user.groups.filter(name='Operateur').exists():
                return redirect('operateur_page')
            elif not request.user.groups.filter(name='Superviseur').exists():
                return redirect('index')
    else:
        form = ReclamationForm()
    return render(request, 'reclamer_lot.html', {'form': form})

def lot_messages(request, lot_ref):
    lot = get_object_or_404(Lot, ref=lot_ref)
    messages = Message.objects.filter(lot=lot).order_by('-temps_reclamation')
    return render(request, 'lot_messages.html', {
        'lot': lot,
        'messages': messages
    })

# Connexion et déconnexion
class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        
        # Redirection en fonction du groupe
        if user.groups.filter(name='Superviseur').exists():
            return redirect('index')
        elif user.groups.filter(name='Operateur').exists():
            return redirect('operateur_page')
        return super().form_valid(form)  # Redirige par défaut si aucun groupe ne correspond

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def operateur_page(request):
    if not request.user.groups.filter(name='Operateur').exists():
        return redirect('login')

    lots = Lot.objects.all()
    processus = Processus.objects.all()

    if request.method == 'POST':
        lot_ref = request.POST.get('lot')
        processus_id = request.POST.get('processus')

        if lot_ref and processus_id:
            lot = get_object_or_404(Lot, ref=lot_ref)
            processus = get_object_or_404(Processus, id=processus_id)

            lot_processus_instance, created = LotProcessus.objects.get_or_create(
                lot=lot,
                processus=processus
            )

            if 'start' in request.POST:
                if not lot_processus_instance.temps_debut:
                    lot_processus_instance.temps_debut = timezone.now()
                    lot_processus_instance.temps_fin = None
                    lot_processus_instance.save()
                    messages.success(request, 'Processus démarré avec succès.')
                else:
                    messages.warning(request, 'Le processus est déjà démarré.')

            elif 'end' in request.POST:
                if lot_processus_instance.temps_debut and not lot_processus_instance.temps_fin:
                    lot_processus_instance.temps_fin = timezone.now()
                    lot_processus_instance.save()
                    messages.success(request, 'Processus terminé avec succès.')
                else:
                    messages.warning(request, 'Le processus doit être démarré avant de le terminer.')

            return redirect('operateur_page')
        else:
            messages.error(request, 'Veuillez sélectionner un lot et un processus.')

    form = ProcessForm()

    return render(request, 'operateur_page.html', {
        'lots': lots,
        'processus': processus,
        'form': form
    })