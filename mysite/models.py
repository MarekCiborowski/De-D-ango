from django.db import models
from django.contrib import admin
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, AbstractUser
)




class wybory(models.Model):
    ID_WYBOROW = models.AutoField(primary_key=True)
    nazwaWyborow = models.CharField(max_length=100)
    maxLiczbaKandydatowDoPoparcia = models.IntegerField()
    dataRozpoczecia = models.DateTimeField()
    dataZakonczenia = models.DateTimeField()

    class Meta:
        ordering = ["ID_WYBOROW"]
        db_table = "Wybory"
        verbose_name = "Wybory"
        verbose_name_plural = "Wybory"


    def getIdWyborow(self):
        return self.ID_WYBOROW

    def getNazwaWyborow(self):
        return self.nazwaWyborow

    def getMaxKandydat(self):
        return self.maxLiczbaKandydatowDoPoparcia

    def getDataRozpoczecia(self):
        return self.dataRozpoczecia

    def getDataZakonczenia(self):
        return self.dataZakonczenia

    def __unicode__(self):
        return self.ID_WYBOROW

    def __str__(self):
        return '%s %s' % (self.ID_WYBOROW, self.nazwaWyborow)


class osoba(models.Model):
    pesel = models.IntegerField(primary_key=True)
    imie = models.CharField(max_length=50)
    nazwisko = models.CharField(max_length=50)
    nr_dowodu = models.CharField(max_length=10)


    class Meta:
        ordering = ["pesel"]
        verbose_name = "Osoba głosująca"
        verbose_name_plural = "Osoby głosujące"
        db_table = "Osoby uprawnione do głosowania"


    def getFullName(self):
        return '%s %s' % (self.imie, self.nazwisko)

    fullName = property(getFullName)

    def getPesel(self):
        return self.pesel

    def __unicode__(self):
        return self.pesel

    def __str__(self):
        return '%s %s %s' % (self.pesel, self.imie, self.nazwisko)





class oddanyGlos(models.Model):
    ID_WYBOROW = models.ForeignKey(wybory, on_delete=models.CASCADE)
    ID_KANDYDATA = models.ForeignKey(osoba, on_delete=models.CASCADE)

    class Meta:
        ordering = ["ID_WYBOROW"]
        verbose_name = "Głos"
        verbose_name_plural = "Głosy"
        db_table = "Głosy"

    def getIdWyborow(self):
        return self.ID_WYBOROW

    def getIdKandydata(self):
        return self.ID_KANDYDATA

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
        unique_together = (("ID_WYBOROW", "pesel"),)

    def getIdWyborow(self):
        return self.ID_WYBOROW

    def getPesel(self):
        return self.pesel

    def isCandidate(self):
        return self.kandydat

    def voted(self):
        return self.oddalGlos

    def __str__(self):
        return '%s %s' % (self.ID_WYBOROW, self.pesel)

