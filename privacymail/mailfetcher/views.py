from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from identity.models import Identity
from mailfetcher.models import Scanword


@staff_member_required
def confirmview(request):
    if request.method == 'POST' and \
        'action' in request.POST and \
            'identity' in request.POST:
        if request.POST['action'] == 'markSpam':
            ident = get_object_or_404(Identity, id=request.POST['identity'])
            ident.receives_third_party_spam = True
            ident.save()
        elif request.POST['action'] == 'markRegistered':
            ident = get_object_or_404(Identity, id=request.POST['identity'])
            ident.approved = True
            ident.save()
        elif request.POST['action'] == 'markPermittedSender':
            ident = get_object_or_404(Identity, id=request.POST['identity'])
            if request.POST['payload'] not in ident.service.permitted_senders:
                ident.service.permitted_senders.append(request.POST['payload'])
                ident.service.save()

    identities = Identity.objects.filter(approved__exact=False)

    return render(request, 'mailfetcher/confirm.html',
                  {'identities': identities})


def wordlistmanager(request):
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'addblacklist' and 'word' in request.POST:
                Scanword.objects.create(type='blacklist', word=request.POST['word'])
            elif request.POST['action'] == 'addlink' and request.POST['word']:
                Scanword.objects.create(type='link', word=request.POST['word'])
            elif request.POST['action'] == 'addname' and request.POST['word']:
                Scanword.objects.create(type='name', word=request.POST['word'])
        elif 'delete' in request.POST:
            Scanword.objects.filter(id=request.POST['delete']).delete()

    subscribe_words = Scanword.objects.filter(type__exact='name')
    subscribe_links = Scanword.objects.filter(type__exact='link')
    subscribe_blacklist = Scanword.objects.filter(type__exact='blacklist')

    return render(request, 'mailfetcher/scanword.html', {
        'word': subscribe_words,
        'link': subscribe_links,
        'blacklist': subscribe_blacklist,
    })
