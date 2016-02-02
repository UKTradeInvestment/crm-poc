from django.shortcuts import render


def organization_view(request):
    return render(
        request,
        'demo/organization.html', {

        }
    )
