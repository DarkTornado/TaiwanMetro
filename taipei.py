import base64, hashlib, hmac, time, json
import requests
import keys
from Crypto.Cipher import AES

def mrt(lineId):
    internalIds = {
        'BR': 'NH',
        'R': 'RG',
        'G': 'GR',
        'O': 'OR',
        'BL': 'BL',
        'Y': 'YL',
    }
    if not internalIds.get(lineId): return []

    id = internalIds[lineId]
    o = base64.b64decode(keys.SECRET_SECOND)
    r = str(int(time.time()))
    a = hmac.new(o, (id + r).encode("utf-8"), hashlib.sha256).hexdigest()

    url = 'https://ws.metro.taipei/cartWeightCore/api/cartweightlocation/getLine'
    headers = {
       "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Mobile Safari/537.36"
    }
    payload = {"service": "cartRoute", "line": id, "time": r, "value": a}

    response = requests.post(url, json=payload, headers=headers)
    data = decrypt_data(lineId, response.text)

    for i, e in enumerate(data):
        updn = e['cDirection']
        status = '도착'
        stn_id = e['cNumberStn']

        if '-' in stn_id:
            stn_ids = stn_id.split('-')
            stn_id = stn_ids[0] if updn == 'up' else stn_ids[1]
            status = '접근'

        # 모든 노선의 상/하행이 반대로 나옴
        updn = 'down' if updn == 'up' else 'up'

        # 신베이터우 지선 (R)
        if lineId == 'R':
            pos = e['cPosition']
            if pos == 200:
                updn = 'down' if updn == 'up' else 'up'
                stn_id = '064b'
                status = '도착'
            elif pos == 201:
                updn = 'down' if updn == 'up' else 'up'
                stn_id = '064b' if updn == 'up' else '065'
                status = '접근'
            elif pos == 202:
                updn = 'down' if updn == 'up' else 'up'
                stn_id = '065'
                status = '도착'

        # 샤오비탄 지선 (G)
        elif lineId == 'G':
            pos = e['cPosition']
            if pos == 302:  # div의 id와 백엔드에서 주는 id가 다름
                updn = 'down' if updn == 'up' else 'up'
                stn_id = '035b'
                status = '도착'
            elif pos == 301:
                updn = 'down' if updn == 'up' else 'up'
                stn_id = '035b' if updn == 'up' else '032'
                status = '접근'
            elif pos == 300:
                updn = 'down' if updn == 'up' else 'up'
                stn_id = '032'
                status = '도착'

        dest_name = e.get('cDestName')
        data[i] = {
            'updn': updn,
            'no': e.get('sPVID') if e.get('sPVID') else e.get('cNumber'),
            'stnId': stn_id,
            'dest': dest_name,
            'status': status,
        }
    
    stns = get_stn_list(lineId)
    result = []
    for stn in stns:
        stn_id = stn['id']
        
        # 해당 역의 id와 일치하는 열차 데이터를 상/하행별로 분류
        up_trains = [
            {'no': e['no'], 'dest': e['dest'], 'status': e['status']}
            for e in data if e.get('stnId') == stn_id and e.get('updn') == 'up'
        ]
        
        down_trains = [
            {'no': e['no'], 'dest': e['dest'], 'status': e['status']}
            for e in data if e.get('stnId') == stn_id and e.get('updn') == 'down'
        ]
        
        result.append({
            'stn': {
                'ko': stn['ko'],
                'tw': stn['tw']
            },
            'up': up_trains,
            'down': down_trains
        })
        
    return result

def decrypt_data(e, i):
    key = base64.b64decode(keys.SECRET_FIRST)
    iv = base64.b64decode(keys.SECRET_THRID)
    ciphertext = base64.b64decode(i)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = cipher.decrypt(ciphertext)
    decrypted_bytes = decrypted_bytes[:-decrypted_bytes[-1]]
    o = decrypted_bytes.decode("utf-8")

    return json.loads(o) if len(o) > 0 and e in ("BR", "Y", "R", "G", "O", "BL") else []

def get_stn_list(lineId):
    if lineId == 'BR': return [
            {'ko': '동물원', 'tw': '動物園', 'id': '019'},
            {'ko': '무자', 'tw': '木柵', 'id': '018'},
            {'ko': '완팡단지', 'tw': '萬芳社區', 'id': '017'},
            {'ko': '완팡병원', 'tw': '萬芳醫院', 'id': '016'},
            {'ko': '신하이', 'tw': '辛亥', 'id': '015'},
            {'ko': '린광', 'tw': '麟光', 'id': '014'},
            {'ko': '류장리', 'tw': '六張犁', 'id': '013'},
            {'ko': '테크놀로지 빌딩', 'tw': '科技大樓', 'id': '012'},
            {'ko': '다안', 'tw': '大安', 'id': '011'},
            {'ko': '중샤오푸싱', 'tw': '忠孝復興', 'id': '010'},
            {'ko': '난징푸싱', 'tw': '南京復興', 'id': '009'},
            {'ko': '중산중학교', 'tw': '中山國中', 'id': '008'},
            {'ko': '송산공항', 'tw': '中山國中', 'id': '007'},
            {'ko': '다즈', 'tw': '大直', 'id': '021'},
            {'ko': '젠난루', 'tw': '劍南路', 'id': '022'},
            {'ko': '시후', 'tw': '西湖', 'id': '023'},
            {'ko': '강첸', 'tw': '港墘', 'id': '024'},
            {'ko': '원더', 'tw': '文德', 'id': '025'},
            {'ko': '네이후', 'tw': '內湖', 'id': '026'},
            {'ko': '다후공원', 'tw': '大湖公園', 'id': '027'},
            {'ko': '후저우', 'tw': '葫洲', 'id': '028'},
            {'ko': '동후', 'tw': '東湖', 'id': '029'},
            {'ko': '난강 소프트웨어 단지', 'tw': '南港軟體園區', 'id': '030'},
            {'ko': '난강전람관', 'tw': '南港展覽館', 'id': '031'}
        ]
    if lineId == 'R': return [
            {'ko': '광츠/펑톈궁', 'tw': '廣慈/奉天宮', 'id': '104'},
            {'ko': '샹산', 'tw': '象山', 'id': '099'},
            {'ko': '타이베이 101/세계무역센터', 'tw': '台北101/世貿', 'id': '100'},
            {'ko': '신이안허', 'tw': '信義安和', 'id': '101'},
            {'ko': '다안', 'tw': '大安', 'id': '011'},
            {'ko': '다안삼림공원', 'tw': '大安森林公園', 'id': '103'},
            {'ko': '동먼', 'tw': '東門', 'id': '134'},
            {'ko': '중정기념당', 'tw': '中正紀念堂', 'id': '042'},
            {'ko': '타이완대학병원', 'tw': '台大醫院', 'id': '050'},
            {'ko': '타이베이역', 'tw': '台北車站', 'id': '051'},
            {'ko': '중산', 'tw': '中山', 'id': '053'},
            {'ko': '솽롄', 'tw': '雙連', 'id': '054'},
            {'ko': '민취안시루', 'tw': '民權西路', 'id': '055'},
            {'ko': '위안산', 'tw': '圓山', 'id': '056'},
            {'ko': '젠탄', 'tw': '劍潭', 'id': '057'},
            {'ko': '스린', 'tw': '士林', 'id': '058'},
            {'ko': '즈산', 'tw': '芝山', 'id': '059'},
            {'ko': '밍더', 'tw': '明德', 'id': '060'},
            {'ko': '스파이', 'tw': '石牌', 'id': '061'},
            {'ko': '치리안', 'tw': '唭哩岸', 'id': '062'},
            {'ko': '치옌', 'tw': '奇岩', 'id': '063'},
            {'ko': '베이터우', 'tw': '北投', 'id': '064'},
            {'ko': '푸싱강', 'tw': '復興崗', 'id': '066'},
            {'ko': '중이', 'tw': '忠義', 'id': '067'},
            {'ko': '관두', 'tw': '關渡', 'id': '068'},
            {'ko': '주웨이', 'tw': '竹圍', 'id': '069'},
            {'ko': '홍수린', 'tw': '紅樹林', 'id': '070'},
            {'ko': '단수이', 'tw': '淡水', 'id': '071'},

            {'ko': '베이터우', 'tw': '北投', 'id': '064b'},
            {'ko': '신베이터우', 'tw': '新北投', 'id': '065'}
        ]
    if lineId == 'G': return [
            {'ko': '신덴', 'tw': '新店', 'id': '033'},
            {'ko': '신덴구청', 'tw': '新店區', 'id': '034'},
            {'ko': '치장', 'tw': '七張', 'id': '035'},
            {'ko': '다핑린', 'tw': '大坪林', 'id': '036'},
            {'ko': '징메이', 'tw': '景美', 'id': '037'},
            {'ko': '완룽', 'tw': '萬隆', 'id': '038'},
            {'ko': '궁관', 'tw': '公館', 'id': '039'},
            {'ko': '대만전력공사빌딩', 'tw': '台電大樓', 'id': '040'},
            {'ko': '구팅', 'tw': '古亭', 'id': '041'},
            {'ko': '중정기념당', 'tw': '中正紀念堂', 'id': '042'},
            {'ko': '샤오난먼', 'tw': '小南門', 'id': '043'},
            {'ko': '시먼', 'tw': '西門', 'id': '086'},
            {'ko': '베이먼', 'tw': '北門', 'id': '105'},
            {'ko': '중산', 'tw': '中山', 'id': '053'},
            {'ko': '쑹장난징', 'tw': '松江南京', 'id': '132'},
            {'ko': '난징푸싱', 'tw': '南京復興', 'id': '009'},
            {'ko': '타이베이 아레나', 'tw': '台北小巨蛋', 'id': '109'},
            {'ko': '난징싼민', 'tw': '南京三民', 'id': '110'},
            {'ko': '쑹산', 'tw': '松山', 'id': '111'},
            
            {'ko': '치장', 'tw': '七張', 'id': '035b'},
            {'ko': '샤오비탄', 'tw': '小碧潭', 'id': '032'}
        ]
    if lineId == 'O': return [
            {'ko': '난스자오', 'tw': '南勢角', 'id': '048'},
            {'ko': '징안', 'tw': '景安', 'id': '047'},
            {'ko': '융안시장', 'tw': '永安市場', 'id': '046'},
            {'ko': '딩시', 'tw': '頂溪', 'id': '045'},
            {'ko': '구팅', 'tw': '古亭', 'id': '041'},
            {'ko': '둥먼', 'tw': '東門', 'id': '134'},
            {'ko': '중샤오신성', 'tw': '忠孝新生', 'id': '089'},
            {'ko': '쑹장난징', 'tw': '松江南京', 'id': '132'},
            {'ko': '싱톈궁', 'tw': '行天宮', 'id': '131'},
            {'ko': '중산초교', 'tw': '中山國小', 'id': '130'},
            {'ko': '민취안시루', 'tw': '民權西路', 'id': '055'},
            {'ko': '다차오터우', 'tw': '大橋頭', 'id': '128'},
            {'ko': '타이베이대교', 'tw': '台北橋', 'id': '127'},
            {'ko': '차이랴오', 'tw': '菜寮', 'id': '126'},
            {'ko': '싼충', 'tw': '三重', 'id': '125'},
            {'ko': '셴써궁', 'tw': '先嗇宮', 'id': '124'},
            {'ko': '터우첸좡', 'tw': '頭前庄', 'id': '123'},
            {'ko': '신좡', 'tw': '新莊', 'id': '122'},
            {'ko': '푸런대학교', 'tw': '輔大', 'id': '121'},
            {'ko': '단펑', 'tw': '丹鳳', 'id': '180'},
            {'ko': '후이룽', 'tw': '迴龍', 'id': '179'},
            {'ko': '싼충초교', 'tw': '三重國小', 'id': '178'},
            {'ko': '싼허중학교', 'tw': '三和國中', 'id': '177'},
            {'ko': '쉬후이고교', 'tw': '徐匯中學', 'id': '176'},
            {'ko': '싼민고교', 'tw': '三民高中', 'id': '175'},
            {'ko': '루저우', 'tw': '蘆洲', 'id': '174'}
        ]
    if lineId == 'BL': return [
            {'ko': '딩푸', 'tw': '頂埔', 'id': '076'},
            {'ko': '융닝', 'tw': '永寧', 'id': '077'},
            {'ko': '투청', 'tw': '土城', 'id': '078'},
            {'ko': '하이산', 'tw': '海山', 'id': '079'},
            {'ko': '야둥병원', 'tw': '亞東醫院', 'id': '080'},
            {'ko': '푸중', 'tw': '府中', 'id': '081'},
            {'ko': '반차오', 'tw': '板橋', 'id': '082'},
            {'ko': '신푸', 'tw': '新埔', 'id': '083'},
            {'ko': '장쯔추이', 'tw': '江子翠', 'id': '084'},
            {'ko': '용산사', 'tw': '龍山寺', 'id': '085'},
            {'ko': '시먼', 'tw': '西門', 'id': '086'},
            {'ko': '타이베이역', 'tw': '台北車站', 'id': '051'},
            {'ko': '산다오사', 'tw': '善導寺', 'id': '088'},
            {'ko': '중샤오신성', 'tw': '忠孝新生', 'id': '089'},
            {'ko': '중샤오푸싱', 'tw': '忠孝復興', 'id': '010'},
            {'ko': '중샤오둔화', 'tw': '忠孝敦化', 'id': '091'},
            {'ko': '국부기념관', 'tw': '國父紀念館', 'id': '092'},
            {'ko': '타이베이시청', 'tw': '市政府', 'id': '093'},
            {'ko': '융춘', 'tw': '永春', 'id': '094'},
            {'ko': '허우산비', 'tw': '後山埤', 'id': '095'},
            {'ko': '쿤양', 'tw': '昆陽', 'id': '096'},
            {'ko': '난강', 'tw': '南港', 'id': '097'},
            {'ko': '난강전람관', 'tw': '南港展覽館', 'id': '031'}
        ]
    if lineId == 'Y': return [
            {'ko': '다핑린', 'tw': '大坪林', 'id': '036'},
            {'ko': '스쓰장', 'tw': '十四張', 'id': '201'},
            {'ko': '슈랑교', 'tw': '秀朗橋', 'id': '202'},
            {'ko': '징핑', 'tw': '景平', 'id': '203'},
            {'ko': '징안', 'tw': '景安', 'id': '047'},
            {'ko': '중허', 'tw': '中和', 'id': '205'},
            {'ko': '차오허', 'tw': '橋和', 'id': '206'},
            {'ko': '중위안', 'tw': '中原', 'id': '207'},
            {'ko': '반신', 'tw': '板新', 'id': '208'},
            {'ko': '반차오', 'tw': '板橋', 'id': '209'},
            {'ko': '신푸민성', 'tw': '新埔民生', 'id': '210'},
            {'ko': '터우첸좡', 'tw': '頭前庄', 'id': '123'},
            {'ko': '싱푸', 'tw': '幸福', 'id': '212'},
            {'ko': '신베이산업단지', 'tw': '新北產業園區', 'id': '213'}
        ]
