# Generated by Django 4.1 on 2024-09-17 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="jenis_pekerjaan",
            fields=[
                (
                    "id_jenis_pekerjaan",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("nama_pekerjaan", models.CharField(max_length=100)),
                (
                    "penghasilan_perbulan",
                    models.DecimalField(decimal_places=2, max_digits=12),
                ),
            ],
        ),
        migrations.CreateModel(
            name="limit_peminjaman",
            fields=[
                (
                    "id_limit_peminjaman",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("nominal_limit", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "id_jenis_pekerjaan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="uang.jenis_pekerjaan",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="nasabah",
            fields=[
                ("id_nasabah", models.AutoField(primary_key=True, serialize=False)),
                ("nama_nasabah", models.CharField(max_length=100)),
                ("umur_nasabah", models.PositiveIntegerField()),
                ("jenis_kelamin", models.CharField(max_length=100)),
                ("alamat_nasabah", models.TextField()),
                ("nama_perusahaan", models.CharField(max_length=100)),
                ("tingkat_pendidikan", models.CharField(max_length=100)),
                ("status_pernikahan", models.BooleanField()),
                ("nama_orang_tua", models.CharField(max_length=100)),
                ("nama_lengkap_kontak_darurat", models.CharField(max_length=100)),
                ("nomor_kontak_darurat", models.PositiveBigIntegerField()),
                ("hubungan_dengan_peminjam", models.CharField(max_length=100)),
                (
                    "sisa_kontrak_kerja",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "id_jenis_pekerjaan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="uang.jenis_pekerjaan",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="peminjaman",
            fields=[
                ("id_peminjaman", models.AutoField(primary_key=True, serialize=False)),
                (
                    "jumlah_pinjaman",
                    models.DecimalField(decimal_places=2, max_digits=12),
                ),
                ("tanggal_pengajuan", models.DateField()),
                ("periode_peminjaman", models.PositiveIntegerField()),
                ("status_pinjaman", models.BooleanField(default=True)),
                (
                    "id_limit_peminjaman",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="uang.limit_peminjaman",
                    ),
                ),
                (
                    "id_nasabah",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="uang.nasabah"
                    ),
                ),
            ],
        ),
    ]
