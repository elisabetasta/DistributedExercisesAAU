from math import sin, cos, pi
from random import randint
from threading import Thread
import tkinter as  TK
import tkinter.ttk as TTK
from os import name

from emulators.SteppingEmulator import SteppingEmulator
from emulators.table import table

def overlay(emulator:SteppingEmulator, run_function):
    # top is planned to be reserved for a little description of controls in stepper
    master = TK.Toplevel()
    height = 500
    width = 500
    spacing = 10

    
    def show_all_data():
        window = TK.Toplevel(master)
        content:list[list] = []
        messages = emulator._list_messages_sent
        message_content = list()
        for message in messages:
            temp = str(message)
            temp = temp.replace(f'{message.source} -> {message.destination} : ', "")
            temp = temp.replace(f'{message.source}->{message.destination} : ', "")
            message_content.append(temp)

        content = [[messages[i].source, messages[i].destination, message_content[i], i] for i in range(len(messages))]
        

        tab = table(window, content, width=15, scrollable="y", title="All messages")
        tab.pack(side=TK.BOTTOM)

        header = TK.Frame(window)
        header.pack(side=TK.TOP, anchor=TK.NW)
        TK.Label(header, text="Source", width=tab.column_width[0]).pack(side=TK.LEFT)
        TK.Label(header, text="Destination", width=tab.column_width[1]).pack(side=TK.LEFT)
        TK.Label(header, text="Message", width=tab.column_width[2]).pack(side=TK.LEFT)
        TK.Label(header, text="Sequence number", width=tab.column_width[3]).pack(side=TK.LEFT)

    def show_data(device_id):
        def _show_data():
            if len(emulator._list_messages_received) > 0:
                window = TK.Toplevel(master)
                window.title(f'Device {device_id}')
                received = list()
                sent = list()
                for message in emulator._list_messages_received:
                    if message.destination == device_id:
                        received.append(str(message))
                    if message.source == device_id:
                        sent.append(str(message))
                if len(received) > len(sent):
                    for _ in range(len(received)-len(sent)):
                        sent.append("")
                elif len(sent) > len(received):
                    for _ in range(len(sent) - len(received)):
                        received.append("")
                content = [[received[i], sent[i]] for i in range(len(received))]

                tab = table(window, content, width=15, scrollable="y", title=f'Device {device_id}')
                tab.pack(side=TK.BOTTOM)

                header = TK.Frame(window)
                header.pack(side=TK.TOP, anchor=TK.NW)
                TK.Label(header, text="Received", width=tab.column_width[0]).pack(side=TK.LEFT)
                TK.Label(header, text="Sent", width=tab.column_width[1]).pack(side=TK.LEFT)
            else:
                return
                
        return _show_data

    def get_coordinates_from_index(center:tuple[int,int], r:int, i:int, n:int) -> tuple[int, int]:
        x = sin((i*2*pi)/n)
        y = cos((i*2*pi)/n)
        if x < pi:
            return int(center[0]-(r*x)), int(center[1]-(r*y))
        else:
            return int(center[0]-(r*-x)), int(center[1]-(r*y))

    def build_device(master:TK.Canvas, device_id, x, y, device_size):
        canvas.create_oval(x, y, x+device_size, y+device_size, outline="black", fill="gray")
        frame = TTK.Frame(master)
        frame.place(x=x+(device_size/8), y=y+(device_size/4))
        TTK.Label(frame, text=f'Device #{device_id}').pack(side=TK.TOP)
        TTK.Button(frame, command=show_data(device_id), text="Show data").pack(side=TK.TOP)
        data_frame = TTK.Frame(frame)
        data_frame.pack(side=TK.BOTTOM)

            

    def stop_emulator():
        emulator.listener.stop()
        emulator.listener.join()
        bottom_label.config(text="Finished running", fg="green")

    def step():
        #insert stepper function
        emulator._single = True
        if emulator.all_terminated():
            bottom_label.config(text="Finished running, kill keyboard listener?... (press any key)")
            Thread(target=stop_emulator).start()
            
        if len(emulator._list_messages_sent) != 0:
            message = emulator._list_messages_sent[len(emulator._list_messages_sent)-1]
            canvas.delete("line")
            canvas.create_line(coordinates[message.source][0]+(device_size/2), coordinates[message.source][1]+(device_size/2), coordinates[message.destination][0]+(device_size/2), coordinates[message.destination][1]+(device_size/2), tags="line")
            msg = str(message)
            msg = msg.replace(f'{message.source} -> {message.destination} : ', "")
            msg = msg.replace(f'{message.source}->{message.destination} : ', "")
            bottom_label.config(text=f'Last message sent: from {message.source} to {message.destination}, content: {msg}')
    def end():
        emulator._stepping = False
        while not emulator.all_terminated():
            pass
        bottom_label.config(text="Finished running, kill keyboard listener?... (press any key)")
        Thread(target=stop_emulator).start()

    canvas = TK.Canvas(master, height=height, width=width)
    canvas.pack(side=TK.TOP)
    device_size = 100
    canvas.create_line(0,0,0,0, tags="line") #create dummy lines
    coordinates:list[tuple[TTK.Label]] = list()
    for device in range(len(emulator._devices)):
        x, y = get_coordinates_from_index((int((width/2)-(device_size/2)), int((width/2)-(device_size/2))), (int((width/2)-(device_size/2)))-spacing, device, len(emulator._devices))
        build_device(canvas, device, x, y, device_size)
        coordinates.append((x,y))


    bottom_frame = TK.LabelFrame(master, text="Inputs")
    bottom_frame.pack(side=TK.BOTTOM)
    TTK.Button(bottom_frame, text="Step", command=step).pack(side=TK.LEFT)
    TTK.Button(bottom_frame, text="End", command=end).pack(side=TK.LEFT)
    TTK.Button(bottom_frame, text="Restart algorithm", command=run_function).pack(side=TK.LEFT)
    TTK.Button(bottom_frame, text="show all Messages", command=show_all_data).pack(side=TK.LEFT)
    bottom_label = TK.Label(master, text="Status")
    bottom_label.pack(side=TK.BOTTOM)
    master.resizable(False,False)
    master.title("Stepping algorithm")