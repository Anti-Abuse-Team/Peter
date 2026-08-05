from dotenv import load_dotenv
from colorama import Fore
import os

load_dotenv()

Enviroment = os.getenv("ENVIROMENT")

if Enviroment == "DEV":
    admin = [
        1491191279479029788, #OVERSEER OF STAFF TEAM
        1491191279479029786, # ASSISTANT OVERSEER OF STAFF TEAM
        1491191279479029785, # AAT STAFF
        1491191279479029784, # AAT DEPUTY STAFF
        1491191279479029783, # ADMIN PERMS
        1491191279479029781 # DEVELOPMENT
    ]

    role_ids = {
        "auth_manager":1491191279353200648,
        "dealing_logs_manager":1491191279353200647,
        "event_manager":1491191279353200646,
        "demo_inspector":1491191279353200645,
        "trial_overseer":1491191279353200645,

        "aat_member":1491191279323713821,
        "trial_aat":1491191279323713820,
        "unoffical_aat":1491191279323713819,

        "auth-1":1491191279152005167,
        "auth-2":1491191279152005169,
        "auth-3":1491191279172718904,
        "auth-4":1491191279172718906,
        "auth-5":1491219568687976489,

        "auth-1_cap":1491191279152005168,
        "auth-2_cap":1491191279172718903,
        "auth-3_cap":1491191279172718905,
        "auth-4_cap":1491191279172718907,

        "officer":0,
        "specialagent":0,
        "agent":0,
        "recruit":0,
        "junioragent":0,
        "senioragent":0,
        "aatsenioragent":0,
        "suspended":0,
        "server_access":0,
        "under_review":0
    }

    channel_ids = {
        "talk-to-peter":1491191282440208514
    }

elif Enviroment == "PRODUCTION":
    admin = [
        1408442799925235794, #OVERSEER OF STAFF TEAM
        1445017368123277460, # ASSISTANT OVERSEER OF STAFF TEAM
        1079504634772738078, # AAT STAFF
        1272691594591473695, # AAT DEPUTY STAFF
        1379137477192843264, # ADMIN PERMS
        1490822155934367796 # DEVELOPMENT

    ]

    role_ids = {
        "auth_manager":1349273782853963828,
        "dealing_logs_manager":1373653657672749096,
        "event_manager":1265028274191339664,
        "demo_inspector":1353346539698917396,
        "trial_overseer":1353346539698917396,

        "aat_member":1079501126262599831,
        "trial_aat":1264027826454003762,
        "unoffical_aat":1264029182183342180,

        "auth-1":1269393495395794954,
        "auth-2":1269393539234529352,
        "auth-3":1269393573929812157,
        "auth-4":1269393602753331202,

        "auth-1_cap":1283446412599885887,
        "auth-2_cap":1283446588261404722,
        "auth-3_cap":1283446785561329696,
        "auth-4_cap":1283446872073179207,

        "officer":1380607532208488548,
        "specialagent":1264707259561410731,
        "agent":1264314593015107746,
        "recruit":1505801392026161195,
        "junioragent":1505801479192051743,
        "senioragent":1505801537521223,
        "aatsenioragent":1505801614047576065,
        "suspended":1323820477130477704,
        "server_access":1354055311060631592,
        "under_review":1323296930310389922
    }

    channel_ids = {
        "talk-to-peter":1264403694615793746
    }



else:
    print(f"{Fore.RED}[-]{Fore.RESET} Failed to load enviroment: {Enviroment}")