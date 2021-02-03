from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from identity.models import Identity


@staff_member_required
def confirmview(request):
    if request.method == 'POST' and request.POST['action'] and request.POST['identity']:
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
                ident.service.permitted_senders.append(
                    request.POST['payload'])
                ident.service.save()

    identities = Identity.objects.filter(
        approved__exact=False
    )

    return render(request, 'mailfetcher/confirm.html', {'identities':
                                                        identities})
