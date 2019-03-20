from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import View
from mailfetcher.models import Mail
from django.shortcuts import get_object_or_404

@staff_member_required
def mailview(request, mail):
    mail = get_object_or_404(Mail, id=mail)
    if request.method == 'POST' and request.POST['action']:
        if request.POST['action'] == 'markSpam':
            for ident in mail.identity.all():
                ident.receives_third_party_spam = True
                ident.save()
        elif request.POST['action'] == 'markRegistered':
            for ident in mail.identity.all():
                ident.approved = True
                ident.save()

    return render(request, 'mailfetcher/mail.html', {'mail': mail})
