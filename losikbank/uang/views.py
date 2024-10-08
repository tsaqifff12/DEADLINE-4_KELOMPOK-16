from django.shortcuts import render, redirect 
from django.http import HttpResponse
from . import models 
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .decorators import role_required

# Create your views here.

def loginview(request) : 
    if request.user.is_authenticated :
        group = None 
        if request.user.groups.exists() : 
            group = request.user.groups.all()[0].name

        if group == 'nasabah' : 
            return redirect('read_peminjaman') 
        elif group in ['admin','owner'] : 
            return redirect('read_peminjaman')
        else :
            return redirect('read_peminjaman')
    else : 
        return render(request, "base/login.html")

def performlogin(request) : 
    if request.method !="POST" :
        return HttpResponse("Method not Allowed")
    else:
        username_login = request.POST['username']
        password_login = request.POST['password'] 
        userobj = authenticate(request, username=username_login, password=password_login)
        if userobj is not None : 
            login(request, userobj) 
            messages.success(request, "Login success")
            if userobj.groups.filter(name='admin').exists() or userobj.groups.filter(name='owner') : 
                return redirect("read_peminjaman") 
            elif userobj.groups.filter(name='nasabah').exists() : 
                return redirect("read_peminjaman")
            elif userobj.groups.filter(name='produksi').exists() :
                return redirect('read_peminjaman')
        else : 
            messages.error(request,"Username atau Password salah !!!")
            return redirect("login") 

@login_required(login_url="login")
def logoutview(request) : 
    logout(request)
    messages.info(request, "Berhasil Logout")
    return redirect('Login')

@login_required(login_url="login")
def performlogout(request) : 
    logout(request)
    return redirect("login")

#CRUD PEMINJAMAN
@role_required(['owner', 'admin', 'nasabah'])
def read_peminjaman(request):
    peminjamanobj = models.peminjaman.objects.all()
    
    if not peminjamanobj.exists():
        messages.error(request, "Data peminjaman tidak ditemukan!")
        return redirect('create_peminjaman')  

    return render(request, 'peminjaman/read_peminjaman.html', {
        'peminjamanobj': peminjamanobj
    })
    

@login_required(login_url='login')
@role_required(['owner', 'admin'])
def create_peminjaman(request):
    if request.method == 'GET':
        return render(request, 'peminjaman/create_peminjaman.html')
    else:
        nama_nasabah = request.POST.get('nama_nasabah')
        nominal_limit = request.POST.get('nominal_limit')
        jumlah_peminjaman = request.POST.get('jumlah_peminjaman')
        tanggal_pengajuan = request.POST.get('tanggal_pengajuan')
        periode_peminjaman = request.POST.get('periode_peminjaman')
        status_peminjaman = request.POST.get('status_peminjaman')
        status_peminjaman = request.POST.get('status_peminjaman', 'off')
        status_peminjaman = True if status_peminjaman == 'on' else False
            
        if not all([nama_nasabah, nominal_limit, jumlah_peminjaman, tanggal_pengajuan, periode_peminjaman, status_peminjaman]):
            messages.error(request, 'Semua kolom wajib diisi!')
            return redirect('create_peminjaman')
        
        try:
            nasabah = models.nasabah.objects.get(nama_nasabah=nama_nasabah)
            limit_peminjaman = models.limit_peminjaman.objects.get(nominal_limit=nominal_limit)
            
            peminjamanobj = models.peminjaman.objects.filter(
                jumlah_peminjaman=jumlah_peminjaman, id_nasabah__nama_nasabah=nama_nasabah
            )
            if peminjamanobj.exists():
                messages.error(request, 'Peminjaman sudah ada!')
                return redirect('create_peminjaman')
            models.peminjaman(
                id_nasabah=nasabah,
                id_limit_peminjaman=limit_peminjaman,
                jumlah_peminjaman=jumlah_peminjaman,
                tanggal_pengajuan=tanggal_pengajuan,
                periode_peminjaman=periode_peminjaman,
                status_peminjaman=status_peminjaman
            ).save()

            messages.success(request, 'Data peminjaman berhasil ditambahkan!')
            return redirect('read_peminjaman')

        except models.nasabah.DoesNotExist:
            messages.error(request, 'Nasabah tidak ditemukan!')
            return redirect('create_peminjaman')
        
        except models.limit_peminjaman.DoesNotExist:
            messages.error(request, 'Limit peminjaman tidak ditemukan!')
            return redirect('create_peminjaman')

        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return redirect('create_peminjaman')

            
@login_required(login_url='login')
@role_required(['owner'])
def update_peminjaman(request, id):
    try:
        nasabahobj = models.nasabah.objects.all()
        getpeminjaman = models.peminjaman.objects.get(id_peminjaman=id)
    except models.peminjaman.DoesNotExist:
        messages.error(request, 'Data peminjaman tidak ditemukan!')
        return redirect('read_peminjaman')

    nama_nasabah = getpeminjaman.id_nasabah.nama_nasabah

    if request.method == 'GET':
        return render(request, 'peminjaman/update_peminjaman.html', {
            'getpeminjaman': getpeminjaman,
            'nama_nasabah': nama_nasabah,
            'nasabahobj': nasabahobj,
            'id': id
        })
    else:
        nama_nasabah = request.POST.get('nama_nasabah')
        nominal_limit = request.POST.get('nominal_limit')
        jumlah_peminjaman = request.POST.get('jumlah_peminjaman')
        tanggal_pengajuan = request.POST.get('tanggal_pengajuan')
        periode_peminjaman = request.POST.get('periode_peminjaman')
        status_peminjaman = request.POST.get('status_peminjaman')
        status_peminjaman = request.POST.get('status_peminjaman', 'off')
        status_peminjaman = True if status_peminjaman == 'on' else False

        try:
            nasabah = models.nasabah.objects.get(nama_nasabah=nama_nasabah)
            
            peminjamanobj = models.peminjaman.objects.filter(
                jumlah_peminjaman=jumlah_peminjaman, id_nasabah__nama_nasabah=nama_nasabah
            )
            if peminjamanobj.exists() and (getpeminjaman.jumlah_peminjaman != jumlah_peminjaman or getpeminjaman.id_nasabah.nama_nasabah != nama_nasabah):

                
                getpeminjaman.id_nasabah = nasabah
                getpeminjaman.id_limit_peminjaman = nominal_limit
                getpeminjaman.jumlah_peminjaman = jumlah_peminjaman
                getpeminjaman.tanggal_pengajuan = tanggal_pengajuan
                getpeminjaman.periode_peminjaman = periode_peminjaman
                getpeminjaman.status_peminjaman = status_peminjaman
                getpeminjaman.save()

                messages.success(request, 'Data peminjaman berhasil diperbarui!')
                return redirect('read_peminjaman')

        except models.nasabah.DoesNotExist:
            messages.error(request, 'Nasabah tidak ditemukan!')
            return redirect('update_peminjaman', id=id)
        
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return redirect('update_peminjaman', id=id)

@login_required(login_url='login')
@role_required(['owner'])
def delete_peminjaman(request, id):
    getpeminjaman = models.peminjaman.objects.get(id_peminjaman = id)
    getpeminjaman.delete()

    messages.error(request, "Data peminjaman berhasil dihapus!")
    return redirect('read_peminjaman')

#CRUD JENIS PEKERJAAN
@login_required(login_url='login')
@role_required(['owner', 'admin', 'nasabah'])
def read_jenis_pekerjaan(request) : 
    jenis_pekerjaanobj = models.jenis_pekerjaan.objects.all()
    if not jenis_pekerjaanobj.exists() : 
        messages.error(request, "Jenis Pekerjaan Tidak Ditemukan!")

    return render(request, 'jenis_pekerjaan/read_jenis_pekerjaan.html', { 
        'jenis_pekerjaanobj' : jenis_pekerjaanobj
    })    

@login_required(login_url='login')
@role_required(['owner'])
def create_jenis_pekerjaan(request):
    if request.method == 'GET':
        return render(request, 'jenis_pekerjaan/create_jenis_pekerjaan.html')

    else:
        nama_pekerjaan = request.POST.get('nama_pekerjaan')
        penghasilan_perbulan = request.POST.get('penghasilan_perbulan')

        if not nama_pekerjaan or not penghasilan_perbulan:
            messages.error(request, 'Nama pekerjaan dan penghasilan per bulan harus diisi.')
            return redirect('create_jenis_pekerjaan')

        try:
            jenis_pekerjaanobj = models.jenis_pekerjaan.objects.filter(nama_pekerjaan=nama_pekerjaan, penghasilan_perbulan=penghasilan_perbulan)
            if jenis_pekerjaanobj.exists():
                messages.error(request, 'Jenis Pekerjaan sudah ada')
                return redirect('create_jenis_pekerjaan')
            else:
                models.jenis_pekerjaan(
                    nama_pekerjaan=nama_pekerjaan,
                    penghasilan_perbulan=penghasilan_perbulan,
                ).save()
                messages.success(request, 'Jenis Pekerjaan berhasil ditambahkan!')
                return redirect('read_jenis_pekerjaan')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {e}')
            return redirect('create_jenis_pekerjaan')

@login_required(login_url='login')
@role_required(['owner'])
def update_jenis_pekerjaan(request, id):
    try :
        getjenis_pekerjaan = models.jenis_pekerjaan.objects.get(id_jenis_pekerjaan=id)
    except models.jenis_pekerjaan.DoesNotExist:
        messages.error(request, 'jenis pekerjaan tidak ditemukan.')
        return redirect('read_jenis_pekerjaan')

    
    if request.method == 'GET':
        return render(request, 'jenis_pekerjaan/update_jenis_pekerjaan.html', {
            'getjenis_pekerjaan': getjenis_pekerjaan,
        })
    
    else:
        nama_pekerjaan = request.POST.get('nama_pekerjaan')
        penghasilan_perbulan = request.POST.get('penghasilan_perbulan')

        if not nama_pekerjaan or not penghasilan_perbulan:
            messages.error(request, 'Nama pekerjaan dan penghasilan per bulan harus diisi.')
            return redirect('update_jenis_pekerjaan', id=id)

        try:
            jenis_pekerjaanobj = models.jenis_pekerjaan.objects.get(nama_pekerjaan=nama_pekerjaan, penghasilan_perbulan=penghasilan_perbulan)
            if getjenis_pekerjaan.nama_pekerjaan == jenis_pekerjaanobj.nama_pekerjaan and getjenis_pekerjaan.penghasilan_perbulan == jenis_pekerjaanobj.penghasilan_perbulan:
                getjenis_pekerjaan.nama_pekerjaan = nama_pekerjaan
                getjenis_pekerjaan.penghasilan_perbulan = penghasilan_perbulan
                getjenis_pekerjaan.save()
                messages.success(request, 'Data Jenis Pekerjaan berhasil diperbarui!')
                return redirect('read_jenis_pekerjaan')
            else:
                messages.error(request, 'Data Jenis Pekerjaan sudah ada!')
                return redirect('update_jenis_pekerjaan', id=id)
            
        except models.jenis_pekerjaan.DoesNotExist:
            getjenis_pekerjaan.nama_pekerjaan = nama_pekerjaan
            getjenis_pekerjaan.penghasilan_perbulan = penghasilan_perbulan
            getjenis_pekerjaan.save()
            messages.success(request, 'Data Jenis Pekerjaan berhasil diperbarui!')
            return redirect('read_jenis_pekerjaan')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {e}')
            return redirect('update_jenis_pekerjaan', id=id)

@login_required(login_url='login')
@role_required(['owner'])
def delete_jenis_pekerjaan(request, id):
    getjenis_pekerjaan = models.jenis_pekerjaan.objects.get(id_jenis_pekerjaan = id)
    getjenis_pekerjaan.delete()

    messages.error(request, "Data Jenis Pekerjaan berhasil dihapus!")
    return redirect('read_jenis_pekerjaan')

#CRUD NASABAH
@login_required(login_url='login')
@role_required(['owner', 'admin', 'nasabah'])
def read_nasabah(request) : 
    nasabahobj = models.nasabah.objects.all()
    if not nasabahobj.exists() : 
        messages.error(request, "Data Nasabah Tidak Ditemukan!")

    return render(request, 'nasabah/read_nasabah.html', { 
        'nasabahobj' : nasabahobj
    })    

@login_required(login_url='login')
@role_required(['owner', 'nasabah'])
def create_nasabah(request):
    if request.method == 'GET':
        return render(request, 'nasabah/create_nasabah.html')

    else:
        nama_pekerjaan = request.POST.get('nama_pekerjaan')
        nama_nasabah = request.POST.get('nama_nasabah')
        umur_nasabah = request.POST.get('umur_nasabah')
        jenis_kelamin = request.POST.get('jenis_kelamin')
        alamat_nasabah = request.POST.get('alamat_nasabah')
        nama_perusahaan = request.POST.get('nama_perusahaan')
        tingkat_pendidikan = request.POST.get('tingkat_pendidikan')
        status_pernikahan = request.POST.get('status_pernikahan', 'off')
        status_pernikahan = True if status_pernikahan == 'on' else False
        nama_orang_tua = request.POST.get('nama_orang_tua')
        nama_lengkap_kontak_darurat = request.POST.get('nama_lengkap_kontak_darurat')
        nomor_kontak_darurat = request.POST.get('nomor_kontak_darurat')
        hubungan_dengan_peminjam = request.POST.get('hubungan_dengan_peminjam')
        sisa_kontrak_kerja = request.POST.get('sisa_kontrak_kerja', None)

        try:
            jenis_pekerjaan_obj = models.jenis_pekerjaan.objects.get(nama_pekerjaan=nama_pekerjaan)
            nasabah = models.nasabah(
                id_jenis_pekerjaan=jenis_pekerjaan_obj,
                nama_nasabah=nama_nasabah,
                umur_nasabah=umur_nasabah,
                jenis_kelamin=jenis_kelamin,
                alamat_nasabah=alamat_nasabah,
                nama_perusahaan=nama_perusahaan,
                tingkat_pendidikan=tingkat_pendidikan,
                status_pernikahan=status_pernikahan,
                nama_orang_tua=nama_orang_tua,
                nama_lengkap_kontak_darurat=nama_lengkap_kontak_darurat,
                nomor_kontak_darurat=nomor_kontak_darurat,
                hubungan_dengan_peminjam=hubungan_dengan_peminjam,
                sisa_kontrak_kerja=sisa_kontrak_kerja if sisa_kontrak_kerja else None
            )
            nasabah.save()
            messages.success(request, 'Data Nasabah berhasil ditambahkan!')
            return redirect('read_nasabah')
        
        except models.jenis_pekerjaan.DoesNotExist:
            messages.error(request, 'Jenis pekerjaan tidak ditemukan.')
            return redirect('create_nasabah')
        
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return redirect('create_nasabah')

@login_required(login_url='login')
@role_required(['owner', 'nasabah'])
def update_nasabah(request, id):
    try:
        getnasabah = models.nasabah.objects.get(id_nasabah=id)
    except models.nasabah.DoesNotExist:
        messages.error(request, 'Nasabah tidak ditemukan.')
        return redirect('read_nasabah')

    if request.method == 'GET':
        return render(request, 'nasabah/update_nasabah.html', {
            'getnasabah': getnasabah,
        })
    
    else:
        nama_pekerjaan = request.POST.get('nama_pekerjaan')
        nama_nasabah = request.POST.get('nama_nasabah')
        umur_nasabah = request.POST.get('umur_nasabah')
        jenis_kelamin = request.POST.get('jenis_kelamin')
        alamat_nasabah = request.POST.get('alamat_nasabah')
        nama_perusahaan = request.POST.get('nama_perusahaan')
        tingkat_pendidikan = request.POST.get('tingkat_pendidikan')
        status_pernikahan = request.POST.get('status_pernikahan', 'off')
        status_pernikahan = True if status_pernikahan == 'on' else False
        nama_orang_tua = request.POST.get('nama_orang_tua')
        nama_lengkap_kontak_darurat = request.POST.get('nama_lengkap_kontak_darurat')
        nomor_kontak_darurat = request.POST.get('nomor_kontak_darurat')
        hubungan_dengan_peminjam = request.POST.get('hubungan_dengan_peminjam')
        sisa_kontrak_kerja = request.POST.get('sisa_kontrak_kerja', '')

        try:
            getnasabah.id_jenis_pekerjaan = models.jenis_pekerjaan.objects.get(nama_pekerjaan=nama_pekerjaan)
            getnasabah.nama_nasabah = nama_nasabah
            getnasabah.umur_nasabah = umur_nasabah
            getnasabah.jenis_kelamin = jenis_kelamin
            getnasabah.alamat_nasabah = alamat_nasabah
            getnasabah.nama_perusahaan = nama_perusahaan
            getnasabah.tingkat_pendidikan = tingkat_pendidikan
            getnasabah.status_pernikahan = status_pernikahan
            getnasabah.nama_orang_tua = nama_orang_tua
            getnasabah.nama_lengkap_kontak_darurat = nama_lengkap_kontak_darurat
            getnasabah.nomor_kontak_darurat = nomor_kontak_darurat
            getnasabah.hubungan_dengan_peminjam = hubungan_dengan_peminjam
            if sisa_kontrak_kerja:
                getnasabah.sisa_kontrak_kerja = sisa_kontrak_kerja
            else:
                getnasabah.sisa_kontrak_kerja = None 
            getnasabah.save()
            
            messages.success(request, 'Data Nasabah berhasil diperbarui!')
            return redirect('read_nasabah')
        
        except models.jenis_pekerjaan.DoesNotExist:
            messages.error(request, 'Jenis pekerjaan tidak ditemukan.')
            return redirect('update_nasabah', id=id)
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return redirect('update_nasabah', id=id)


@login_required(login_url='login')
@role_required(['owner'])
def delete_nasabah(request, id):
    getnasabah = models.nasabah.objects.get(id_nasabah = id)
    getnasabah.delete()

    messages.error(request, "Data Nasabah berhasil dihapus!")
    return redirect('read_nasabah')

#CRUD LIMIT PEMINJAMAN
@login_required(login_url='login')
@role_required(['owner', 'admin', 'nasabah'])
def read_limit_peminjaman(request) : 
    limit_peminjamanobj = models.limit_peminjaman.objects.all()
    if not limit_peminjamanobj.exists() : 
        messages.error(request, "Limit Peminjaman tidak ditemukan!")

    return render(request, 'limit_peminjaman/read_limit_peminjaman.html', { 
        'limit_peminjamanobj' : limit_peminjamanobj
    })    

@login_required(login_url='login')
@role_required(['owner','admin'])
def create_limit_peminjaman(request):
    jenis_pekerjaanobj = models.jenis_pekerjaan.objects.all()
    if request.method == 'GET':
        return render(request, 'limit_peminjaman/create_limit_peminjaman.html', {
            'jenis_pekerjaanobj' : jenis_pekerjaanobj
        })

    else :
        nama_pekerjaan = request.POST.get('nama_pekerjaan')
        nominal_limit = request.POST.get('nominal_limit')

        part1, part2 = nama_pekerjaan.split(' - ')

        part1 = part1.strip()
        part2 = int(part2.strip())

        getlimitpeminjaman = models.jenis_pekerjaan.objects.get(nama_pekerjaan = part1, penghasilan_perbulan = part2)
        limitpeminjamanobj = models.limit_peminjaman.objects.filter(id_jenis_pekerjaan = getlimitpeminjaman)

        if limitpeminjamanobj.exists() :
            messages.error(request, 'Data Limit Peminjaman Sudah Ada!')
            return redirect('create_limit_peminjaman')

        else :
            models.limit_peminjaman(
                id_jenis_pekerjaan = models.jenis_pekerjaan.objects.get(nama_pekerjaan = part1, penghasilan_perbulan = part2),
                nominal_limit = nominal_limit,
            ).save()
            messages.success(request, 'Limit Pekerjaan berhasil ditambahkan!')
            return redirect('read_limit_peminjaman')

@login_required(login_url='login')
@role_required(['owner','admin'])
def update_limit_peminjaman(request, id):
    getlimit_peminjaman = models.limit_peminjaman.objects.get(id_limit_peminjaman = id)
    if request.method == 'GET':
        return render(request, 'limit_peminjaman/update_limit_peminjaman.html', {
            'getlimit_peminjaman' : getlimit_peminjaman,
        })
    
    else :
        nominal_limit = request.POST.get('nominal_limit')
        getlimit_peminjaman.id_limit_peminjaman = getlimit_peminjaman.id_limit_peminjaman
        getlimit_peminjaman.nominal_limit = nominal_limit
        getlimit_peminjaman.save()
        messages.success(request, 'Data Limit Peminjaman berhasil diperbarui!')
        return redirect('read_limit_peminjaman')

@login_required(login_url='login')
@role_required(['owner'])
def delete_limit_peminjaman(request, id):
    getlimit_peminjaman = models.limit_peminjaman.objects.get(id_limit_peminjaman = id)
    getlimit_peminjaman.delete()

    messages.error(request, "Data Limit Peminjaman berhasil dihapus!")
    return redirect('read_limit_peminjaman')
