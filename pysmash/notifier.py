from _thread import start_new_thread

from pysmash import SmashGG
from twilio.rest import Client
from tkinter import *

smash = SmashGG() # needed to use smash.gg api
client = Client("AC214be4c9c0197514d5b991494db67016", "08fb138a63f1d77825818aadd074cf36") # needed to send messages using twilio

root = Tk() # tkinter root node
l1 = Label(root, text="Player-tag (CASE SENSITIVE)\n")
l1.grid(row=0,column=0)
e1 = Entry(root)
e1.grid(row=0,column=1)
l2 = Label(root, text="Tournament name (Taken from smashgg url, see doc for specific)\n")
l2.grid(row=1,column=0)
e2 = Entry(root)
e2.grid(row=1,column=1)
l3 = Label(root, text="Event name (Taken from smashgg url)\n")
l3.grid(row=2,column=0)
e3 = Entry(root)
e3.grid(row=2,column=1)
l4 = Label(root, text="Phone Number including + and national code(format: +xxxxxxxxxxx)")
l4.grid(row=3, column=0)
e4 = Entry(root)
e4.grid(row=3, column=1)


def get_message():
    """
    method for fetching the player-tag, tournament, and event as well as locking entries once data has been entered
    :return: player-tag, tournament-name, and event-name
    """
    #disable the labels then return their contents
    e1.config(state='readonly')
    e2.config(state='readonly')
    e3.config(state='readonly')
    e4.config(state='readonly')
    return e1.get(), e2.get(), e3.get()


def get_phone_number():
    """
    :return: phone number from label
    """
    return e4.get()


def print_message():
    print(get_message())


def message_loop():
    print_message()
    root.after(5000, message_loop)


def check_for_unplayed():
    """
    fetches information from the tkinter entries and then queries the smash.gg api to see whether the player has a match that they must start
    :return: whether the player has a match that they must play
    """
    player_tag, tournament_name, event_name = get_message()
    sets = smash.tournament_show_player_sets(tournament_name=tournament_name, player_tag=player_tag, event=event_name, filter_completed=True, filter_future=True, filter_current=False)
    only_sets = sets['sets']
    for set in only_sets:
        if not set['entrant_1_id'] is None and not set['entrant_2_id'] is None: #set has 2 entrants
            if set['winner_id'] == 'None' and set['loser_id'] == 'None': #set does not yet have a winner and loser
                if set['entrant_1_score'] is None and set['entrant_2_score'] is None: #set has also not yet started, because there is no score
                    return True
    return False #if we reach the end of the loop, there were no unplayed sets


def check_and_notify():
    """
    recursive function that checks whether the player has a match they must start. if they do, they are sent a text message to their entered phone number.
    :return:
    """
    b.config(state='disabled')
    player_tag = e1.get()
    event_name = e3.get()
    if check_for_unplayed(): #we need to send a message
        message_body = "Hey " + player_tag + ", you have an unplayed match for " + event_name + "! \n -smashnotify <3"
        client.messages.create(to=get_phone_number(), from_="+12016454023", body=message_body)
        #we are in a set and have sent a message, so we can wait a longer time (10 minutes) before reminding
        root.after(600000, check_and_notify)
    else:
        root.after(300000, check_and_notify) #we were not in a set, so need to check again sooner (5 minutes)



b = Button(root, text="remind", width=10, command=check_and_notify) #button to start checking and notifying
b2 = Button(root, text="quit", width=10, command=sys.exit) #button to exit - stops the loop and the program
b.grid(row=4,column=0)
b2.grid(row=4,column=1)

root.title("Smashnotify")
root.iconbitmap('smash.ico')
root.mainloop()

