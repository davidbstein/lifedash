
######################
## FITNESS TRACKING ##
######################

SECRETS = json.load(open('secrets.json', 'r'))

s = requests.session()

login_page = s.get("https://sso.garmin.com/sso/signin?service=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&webhost=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&source=https%3A%2F%2Fconnect.garmin.com%2Fsignin%2F&redirectAfterAccountLoginUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&redirectAfterAccountCreationUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&gauthHost=https%3A%2F%2Fsso.garmin.com%2Fsso&locale=en_US&id=gauth-widget&cssUrl=https%3A%2F%2Fconnect.garmin.com%2Fgauth-custom-v1.2-min.css&privacyStatementUrl=https%3A%2F%2Fwww.garmin.com%2Fen-US%2Fprivacy%2Fconnect%2F&clientId=GarminConnect&rememberMeShown=true&rememberMeChecked=false&createAccountShown=true&openCreateAccount=false&displayNameShown=false&consumeServiceTicket=false&initialFocus=true&embedWidget=false&generateExtraServiceTicket=true&generateTwoExtraServiceTickets=false&generateNoServiceTicket=false&globalOptInShown=true&globalOptInChecked=false&mobile=false&connectLegalTerms=true&showTermsOfUse=false&showPrivacyPolicy=false&showConnectLegalAge=false&locationPromptShown=true&showPassword=true&useCustomHeader=false#")



t = login_page.text
csrf_idx = t.index('_csrf" value="') + len('_csrf" value="')
csrf = t[csrf_idx:csrf_idx+100]



attempt = s.post(garminURI, {
    "username": SECRETS['GARMIN']['email'],
    "password": SECRETS['GARMIN']['pass'],
    'csrf': csrf,
    'embed': False
})


from IPython.core.display import HTML
HTML(attempt.text)

######################
# LOCATION TRACKING ##
######################
#from ..scrapers import location
#location_data = caching.get_or_reload('location', location._get_locations, 10)
#write_to_www('location', location_data, title="Location")

