import tkinter as tk

def onClick():
    print("onClick")

root = tk.Tk()
root.title("MangaManager")

lbl = tk.Label(root,text = "label 1")
lbl.grid(row=0, column=0)

btn = tk.Button(root, text = "button",command=onClick)
btn.grid(row=100,column=1000)
root.mainloop()
