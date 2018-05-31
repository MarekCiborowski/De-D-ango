from django.db import models
from django.contrib import admin
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, AbstractUser,
    User)
from django.db.models.signals import post_save
from django.dispatch import receiver


class myUser(AbstractUser):
    is_mod = models.BooleanField(default=False)


class wybory(models.Model):
    ID_WYBOROW = models.AutoField(primary_key=True)
    nazwaWyborow = models.CharField(max_length=100)
    maxLiczbaKandydatowDoPoparcia = models.PositiveIntegerField()
    dataRozpoczecia = models.DateTimeField()
    dataZakonczenia = models.DateTimeField()

    class Meta:
        ordering = ["ID_WYBOROW"]
        db_table = "Wybory"
        verbose_name = "Wybory"
        verbose_name_plural = "Wybory"

    def __unicode__(self):
        return self.ID_WYBOROW

    def __str__(self):
        return '%s %s' % (self.ID_WYBOROW, self.nazwaWyborow)


class osoba(models.Model):

    user = models.OneToOneField(myUser, on_delete=models.CASCADE, null=True, related_name='user_profile')

    pesel = models.IntegerField(primary_key=True)
    imie = models.CharField(max_length=50)
    nazwisko = models.CharField(max_length=50)
    nr_dowodu = models.CharField(unique=True, max_length=10)

    class Meta:
        ordering = ["pesel"]
        verbose_name = "Osoba głosująca"
        verbose_name_plural = "Osoby głosujące"
        db_table = "Osoby uprawnione do głosowania"

    def __unicode__(self):
        return self.pesel

    def __str__(self):
        return '%s %s %s' % (self.pesel, self.imie, self.nazwisko)


class Mod(models.Model):
    user = models.OneToOneField(myUser, on_delete=models.CASCADE, null=True, related_name='mod_profile', unique=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)


class oddanyGlos(models.Model):
    ID_WYBOROW = models.ForeignKey(wybory, on_delete=models.CASCADE)
    ID_KANDYDATA = models.ForeignKey(osoba, on_delete=models.CASCADE)

    class Meta:
        ordering = ["ID_WYBOROW"]
        verbose_name = "Głos"
        verbose_name_plural = "Głosy"
        db_table = "Głosy"

    def __unicode__(self):
        return u'%s %s' % (self.ID_WYBOROW, self.ID_KANDYDATA)

    def __str__(self):
        return '%s %s' % (self.ID_WYBOROW, self.ID_KANDYDATA)


class osobaWybory(models.Model):
    ID_WYBOROW = models.ForeignKey(wybory, on_delete=models.CASCADE)
    pesel = models.ForeignKey(osoba, on_delete=models.CASCADE)
    kandydat = models.BooleanField(default=False)
    oddalGlos = models.BooleanField(default=False)

    class Meta:
        db_table = "Osoba-Wybory"

    def __str__(self):
        return '%s %s' % (self.ID_WYBOROW, self.pesel)

