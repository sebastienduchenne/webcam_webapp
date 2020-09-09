-ouvrir une invite de commande
cd C:\Users\sduchenn\Documents\MesDocs\RetD - HERA\workspace\spectrogramme


-intaller librosa
pip install librosa


-installer matplotlib
pip install matplotlib


-Lancer le programme
python spectrogramme.py <nom wav>





n_fft : netteté
    =2048 : trop flou, mettre 1024
    =512 : trait noir horizontal
    =1024 : OK, un peu flou
    =800: ok, net

hop_length : résolution
    = 1024 : très pixelisé
    = 128 : ok
    = 80 : comme 128

n_mels : luminosité
    = 256
    = 1024 : assez sombre