#!/usr/bin/env python
import urllib, re, os, sys, time

import pygtk
pygtk.require('2.0')
import gtk
import gnome
import gnomeapplet
import gobject


class NetBenefitsApplet(gnomeapplet.Applet):
    signUP = "/\\"
    signDOWN = "\\/"
    
    def __init__(self,applet,iid):
        self.timeout_interval = 60000 # 60 secs
        self.sign = ""
        self.fetch_info(prev=False)
	
        self.__gobject_init__()
        
        gnome.init("Netbenefits applet", "0.2")
        self.applet=applet
        self.evbox = gtk.EventBox()
        self.orientation = self.applet.get_orient()

        self.box = None

        if self.orientation == gnomeapplet.ORIENT_UP or \
            self.orientation == gnomeapplet.ORIENT_DOWN:
            self.box = gtk.HBox()
        else:
            self.box = gtkVBox()

        self.evbox.add(self.box)

        self.box.pack_start(gtk.EventBox())
        self.box.get_children()[0].add(gtk.HBox())

        lbl=gtk.Label(str(self.stock_volume*self.current_price) + "CZK")
        self.box.get_children()[0].get_children()[0].pack_start(lbl)
	

        self.box.show()
        self.applet.add(self.evbox)
        self.applet.show_all()


        gobject.timeout_add(self.timeout_interval, self.timeout_callback, self)

    def fetch_info(self, prev=True):
        self.stock_volume=get_stock_volume()

        if prev:
            self.prev_stock_price = self.stock_price

        self.stock_price = get_quote("RHT")
        self.current_price =  round((self.stock_price * get_cnb_value("USD")))

    def timeout_callback(self,event):
        self.fetch_info()

        for i in (self.box.get_children()):
                self.box.remove(i)

        self.box.pack_start(gtk.EventBox())
        self.box.get_children()[0].add(gtk.HBox())

        sign = ""
        if self.prev_stock_price > self.stock_price:
            sign = self.signDOWN
        elif self.prev_stock_price < self.stock_price:
            sign = self.signUP

        lbl=gtk.Label(sign + str(self.stock_volume*self.current_price) + "CZK")
        self.box.get_children()[0].get_children()[0].pack_start(lbl)
        
        self.applet.show_all()
        return 1

        
def get_stock_volume():
    try:
        f=open("%s/.netbenefits" % os.getenv("HOME"), "r")
        stock_volume=float(f.readline().strip().replace(",", "."))
        f.close()

        return stock_volume

    except IOError:
        sys.stderr.write("Failed to open ~/.netbenefits.  Setting volume to 0.0.\n") 
        return 0.0

    except ValueError:
        sys.stderr.write("Unexpected value in ~/.netbenefits. Expected type is int/float. Setting volume to 0.0.\n") 
        return 0.0

def get_quote(symbol):
    base_url = 'http://www.nasdaq.com/aspx/infoquotes.aspx?symbol='
    try:
        content = urllib.urlopen(base_url + symbol).read()
        m = re.search("_LastSale1'>\$&nbsp;([0-9]+.[0-9]+)</label>",content)
        if m:
            quote = m.group(1)
        else:
            value = 0.0

        return float(quote)

    except IOError:
        sys.stderr.write("Failed to fetch data from nasdaq.com")
        return 0.0


def get_cnb_value(currency):
    t = time.gmtime()
    curr_date="%d.%d.%d" % (t[2], t[1], t[0])
    base_url = 'http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.txt?date='
    try:
        content = urllib.urlopen(base_url + curr_date).read()
        match=re.search("[a-zA-Z]\|[a-zA-Z]+\|[0-9]+\|%s+\|([0-9,]+)" % (currency), content)
        if match:
            value = float(match.group(1).replace(",", "."))

        else:
            value = 0.0

        return value

    except IOError:
        sys.stderr.write("Failed to fetch data from cnb.cz")
        return 0.0
    
def nb_factory(applet, iid):
    NetBenefitsApplet(applet,iid)
    return gtk.TRUE

def main():
        gnomeapplet.bonobo_factory("OAFIID:GNOME_NetbenefitsApplet_Factory", 
                                     NetBenefitsApplet.__gtype__, 
                                     "netbenefits", "0", nb_factory)

if len(sys.argv) > 1 and sys.argv[1] == "run-in-window":
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("NetBenefits Applet")
    main_window.connect("destroy", gtk.main_quit)
    app = gnomeapplet.Applet()
    nb_factory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()

if __name__ == '__main__':
    main()

