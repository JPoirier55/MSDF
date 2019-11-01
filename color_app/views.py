from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from color_app import util


def index(request):
    return render(request, 'index.html')


def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'upload.html')


def process(request):
    fs = FileSystemStorage()
    p = Path(fs.location)
    files_full = list(p.glob('**/*'))
    file_urls = []
    processed = []
    for f in files_full:
        if f.is_file():
            if "_meanshift" not in str(f):
                file_url = "/".join(str(f).split("\\")[-2:])
                file_urls.append(file_url)
            else:
                file_url = "/".join(str(f).split("\\")[-3:])
                processed.append(file_url)
    return render(request, 'process.html', {'file_urls': file_urls,
                                            'processed': processed})


def process_dmc(request):
    fs = FileSystemStorage()
    p = Path(fs.location)
    files_full = list(p.glob('**/*'))
    file_urls = []
    processed = []
    for f in files_full:
        if f.is_file():
            if "_dmc" not in str(f):
                file_url = "/".join(str(f).split("\\")[-2:])
                file_urls.append(file_url)
            else:
                file_url = "/".join(str(f).split("\\")[-3:])
                processed.append(file_url)
    return render(request, 'process_dmc.html', {'file_urls': file_urls,
                                            'processed': processed})


def process_api(request):
    file = request.GET.get('filename', None)
    print(file)
    if file:
        newfile = util.process_meanshift(file)
        return HttpResponse(newfile)
    else:
        return HttpResponse('null')


def process_dmc_api(request):
    file = request.GET.get('filename', None)
    print(file)
    if file:
        newfile = util.process_dmc(file)
        return HttpResponse(newfile)
    else:
        return HttpResponse('null')

