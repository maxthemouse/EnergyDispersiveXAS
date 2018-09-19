#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from nei import *
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import threading


class NearEdgeImaging:
    """docstring for NearEdgeImaging"""

    def __init__(self):
        #################### create some ttk styles     ######################
        # s = ttk.Style()
        # s.configure("Small.TNotebook.Tab", padding=[25,5])
        # # s.configure("BW.TNotebook.Tab", padding=[157,5])
        # # s.configure('Kim.TNotebook.Tab', padding=[25,5])


        #################### Start window   ##################################
        window = Tk()
        window.minsize(width=800, height=500)
        window.title("Near Edge Imaging")

        master = ttk.Notebook(window)
        # master.pack(expand=1, fill="both")
        master.grid()


        #################   Frame 1   ##########################################
        tabKES = ttk.Frame(master)
        frame1 = LabelFrame(tabKES,bd=4,relief=RIDGE,
                            text = "STEP 1: SETUP PARAMETERS\n(Use default if you are not sure what they are)",
                            font = ('Helvetica', '11'),labelanchor=N)
        frame1.pack(pady=12)
        # use file
        self.use_file = BooleanVar()
        cbtUseFile = Checkbutton(frame1, text="Use File", variable=self.use_file)
        self.use_file.set(True)
        self.lowpass = BooleanVar()
        cbtLowpass = Checkbutton(frame1, text="Lowpass Filter", variable=self.lowpass)

        # multislice
        self.multislice = BooleanVar()
        cbtMultislice = Checkbutton(frame1, text='Multiple Slices', variable=self.multislice,
                                    command=self.sliceState)
        self.multislice.set(True)
        labelProj = Label(frame1, text="Number of Projections")
        self.nproj = IntVar()
        self.entryNproj = Entry(frame1, textvariable=self.nproj,
                                state=NORMAL if self.multislice.get() else DISABLED)
        self.nproj.set(900)
        labelSlice = Label(frame1, text='Slice No.')
        self.slice = IntVar()
        self.entrySlice = Entry(frame1, textvariable=self.slice,
                                state=NORMAL if self.multislice.get() else DISABLED)
        self.slice.set(0)

        # ct correction
        self.ct = BooleanVar()
        cbtCTcorrection = Checkbutton(frame1, text='Correction with Side Pixels',
                                      variable=self.ct, command=self.sideWidthState)
        self.ct.set(True)
        labelSideWidth = Label(frame1, text='Side Width (Pixels)')
        self.side_width = IntVar()
        self.entrySideWidth = Entry(frame1, textvariable=self.side_width,
                                    state=NORMAL if self.ct.get() else DISABLED)
        self.side_width.set(50)

        # energy range
        self.e_range = BooleanVar()
        cbtRange = Checkbutton(frame1, text='Energy Range', variable=self.e_range,
                               command=self.erangeState)
        self.e_range.set(False)
        self.e_low = DoubleVar()
        self.e_high = DoubleVar()
        labelElow = Label(frame1, text='Min(keV)')
        self.entryElow = Entry(frame1, textvariable=self.e_low,
                               state=NORMAL if self.e_range.get() else DISABLED)
        labelEhigh = Label(frame1, text='Max(keV)')
        self.entryEhigh = Entry(frame1, textvariable=self.e_high,
                                state=NORMAL if self.e_range.get() else DISABLED)

        # use torch
        self.use_torch = BooleanVar()
        cbtTorch = Checkbutton(frame1, text="Torch.Tensor", variable=self.use_torch)
        self.use_torch.set(True)

        # fix vertical motion
        self.fix_vertical_motion = BooleanVar()
        cbtFixVertical = Checkbutton(frame1, text='Fix Vertical Motion', variable=self.fix_vertical_motion)
        self.fix_vertical_motion.set(True)

        # snr
        self.snr = BooleanVar()
        cbtSNR = Checkbutton(frame1, text='Calculate SNR', variable=self.snr)
        self.snr.set(False)

        # algorithm
        labelAlgo = Label(frame1, text='Algorithm')
        self.algorithm = StringVar()
        rbtAlgo1 = Radiobutton(frame1, text='sKES Equation', variable=self.algorithm,
                               value='sKES_equation')
        rbtAlgo2 = Radiobutton(frame1, text='nnls', variable=self.algorithm, value='nnls')
        self.algorithm.set('sKES_equation')

        cbtUseFile.grid(row=1, column=0, sticky=W)
        cbtLowpass.grid(row=2, column=0, sticky=W)
        cbtMultislice.grid(row=3, column=0, sticky=W)
        labelProj.grid(row=3, column=1)
        self.entryNproj.grid(row=3, column=2)
        labelSlice.grid(row=3, column=3)
        self.entrySlice.grid(row=3, column=4)
        cbtCTcorrection.grid(row=4, column=0, sticky=W)
        labelSideWidth.grid(row=4, column=1, sticky=E)
        self.entrySideWidth.grid(row=4, column=2)
        cbtRange.grid(row=5, column=0, sticky=W)
        labelElow.grid(row=5, column=1, sticky=E)
        self.entryElow.grid(row=5, column=2)
        labelEhigh.grid(row=5, column=3)
        self.entryEhigh.grid(row=5, column=4)
        cbtTorch.grid(row=6, column=0, sticky=W)
        cbtFixVertical.grid(row=7, sticky=W)
        cbtSNR.grid(row=8, sticky=W)
        labelAlgo.grid(row=9, sticky=W)
        rbtAlgo1.grid(row=9, column=1, sticky=W)
        rbtAlgo2.grid(row=9, column=2, sticky=W)

        ####################### frame 1.recon  #######################
        frameRecon = Frame(frame1)
        frameRecon.grid(row=10, rowspan=3, columnspan=5, sticky=W)

        self.do_recon = BooleanVar()
        cbtRecon = Checkbutton(frameRecon, text='Reconstruction', variable=self.do_recon,
                               command=self.reconState)
        self.do_recon.set(False)
        # labelRecon = Label(frameRecon, text='Reconstruction')

        self.recon = StringVar()
        # rbtRecon0 = Radiobutton(frameRecon, text='No', variable=self.recon, value='No')
        self.rbtRecon1 = Radiobutton(frameRecon, text='SKIMAGE', variable=self.recon, value='skimage',
                                     state=NORMAL if self.do_recon.get() else DISABLED)
        self.rbtRecon2 = Radiobutton(frameRecon, text='IDL', variable=self.recon, value='idl',
                                     state=NORMAL if self.do_recon.get() else DISABLED)
        self.recon.set(None)
        self.center = IntVar()
        labelCenter = Label(frameRecon, text='Rotation Center')
        self.entryCenter = Entry(frameRecon, textvariable=self.center,
                                 state=NORMAL if self.do_recon.get() else DISABLED)
        self.center.set(0)

        # labelRecon.grid(row=0, sticky=W)
        cbtRecon.grid(row=0, column=0, sticky=W)
        self.rbtRecon1.grid(row=0, column=1, sticky=W)
        self.rbtRecon2.grid(row=0, column=2, sticky=W)
        labelCenter.grid(row=0, column=4)
        self.entryCenter.grid(row=0, column=5)

        ########################  frame 2  ###########################
        # Label(master, text='STEP 2: LOAD DATA and PRAY').grid(pady=15)
        frame2 = LabelFrame(tabKES, text = 'STEP 2: LOAD DATA and PRAY',font = ('Helvetica', '11'),
                            bd=4, relief=RIDGE,labelanchor=N)
        frame2.pack(ipadx=4)
        self.curr_path = os.getcwd()
        labelPath = Label(frame2, text="Data Directory")
        self.path = StringVar()
        entryPath = Entry(frame2, textvariable=self.path, width=75)
        btBrowse = Button(frame2, text="Browse", command=self.browseData)
        self.path.set(self.curr_path)

        labelPath.grid(sticky=W)
        entryPath.grid(row=0, column=1, padx=3)
        btBrowse.grid(row=0, column=2)

        labelSavePath = Label(frame2, text='Save Directory')
        self.save_path = StringVar()
        entrySavePath = Entry(frame2, textvariable=self.save_path, width=75)
        btBrowse2 = Button(frame2, text="Browse", command=self.browseSave)
        self.save_path.set(self.curr_path)

        labelSavePath.grid(row=1, sticky=W)
        entrySavePath.grid(row=1, column=1, padx=3)
        btBrowse2.grid(row=1, column=2)

        btRun = Button(frame2, height=2, width=30, text='MAY THE EDGE BE WITH ME',
                       bg='purple4', fg='snow', cursor='pirate', command=self.run)
        Button.config(btRun, font=('Helvetica', '11'))
        btRun.grid(row=2, columnspan=3)

        ###################  Frame3:  Reconstruction   #############################
        # Label(master, text='CT RECONSTRUCTION').grid(row=0, column=1, pady=15)
        tabRecon = ttk.Frame(master)
        frame3 = LabelFrame(tabRecon, text = 'Control',bd=4, relief=GROOVE,labelanchor=N)
        frame3.grid(row=0, column=0, sticky=NS)
        Label(frame3, text='').grid()

        frame3_1 = Frame(frame3)
        frame3_1.grid(sticky=W)
        Label(frame3_1, text='Load Sinogram', width=15).grid(row=0, sticky=W)
        btLoad = Button(frame3_1, text='Browse', command=self.browseSino).grid(row=0, column=1)
        # combobox(下拉列表) for choosing the target sinogram
        self.sino_index = '0'
        self.target_sino_id = StringVar()
        self.target_sino_id.set('0')
        self.cboxTarget = ttk.Combobox(frame3_1, width=6, textvariable=self.target_sino_id,
                                       state='disabled')
        self.cboxTarget.grid(row=0, column=2, padx=12)
        self.cboxTarget['values'] = ('0')
        self.cboxTarget.current(0)
        self.update_cbox = False  # Nothing has been loaded yet
        # Button to show selected sinogram
        self.btShowSino = Button(frame3_1, text='Show Selected', command=self.selectSino, state=DISABLED)
        self.btShowSino.grid(row=0, column=3)

        frame3_3 = Frame(frame3)
        frame3_3.grid(sticky=W)
        Label(frame3_3, text='Function', width=15).grid()
        self.reconFunc = StringVar()
        self.rbtReconSK = Radiobutton(frame3_3, text='SKIMAGE', variable=self.reconFunc, value='skimage')
        self.rbtReconIDL = Radiobutton(frame3_3, text='IDL', variable=self.reconFunc, value='idl')
        self.reconFunc.set('skimage')
        self.rbtReconSK.grid(row=0, column=1)
        self.rbtReconIDL.grid(row=0, column=2)

        frame3_4 = Frame(frame3)
        frame3_4.grid(sticky=W)
        self.rotCenter = IntVar()
        labelCenter2 = Label(frame3_4, text='Rotation Center', width=15).grid()
        self.entryCenter2 = Entry(frame3_4, textvariable=self.rotCenter)
        self.entryCenter2.grid(row=0, column=1)
        self.center.set(0)

        frame3_5 = Frame(frame3)
        frame3_5.grid(sticky=W)
        labelPixel = Label(frame3_5, text='Pixel Size(um)', width=15).grid()
        self.pixel = DoubleVar()
        entryPixel = Entry(frame3_5, textvariable=self.pixel).grid(row=0, column=1)
        rbtPixel_9 = Radiobutton(frame3_5, text='9um', variable=self.pixel, value=9).grid(row=0, column=2)
        rbtPixel_13 = Radiobutton(frame3_5, text='13.6um', variable=self.pixel, value=13.6).grid(row=0, column=3)
        self.pixel.set(13.6)

        frame3_6 = Frame(frame3)
        frame3_6.grid(sticky=W)
        Label(frame3_6, text='Save Directory', width=15).grid()
        self.recon_path = StringVar()
        frame3_6_1 = Frame(frame3)
        frame3_6_1.grid(sticky=EW)
        for x in range(10):  # configure the columns to have a non-zero weight
            Grid.columnconfigure(frame3_6_1, x, weight=1)
        entryReconPath = Entry(frame3_6_1, textvariable=self.recon_path) \
            .grid(columnspan=10, sticky=EW, padx=6)
        btReconPath = Button(frame3_6, text='Browse', command=self.browseReconPath).grid(row=0, column=1)
        self.auto_save = BooleanVar()
        self.color_auto_save = StringVar()
        self.color_auto_save.set('gray70')
        self.cbtAutoSave = Checkbutton(frame3_6, text='Auto Save', variable=self.auto_save,
                                       bg=self.color_auto_save.get(), command=self.AutoSave)
        self.cbtAutoSave.grid(row=0, column=2,padx=7)
        self.auto_save.set(False)

        frame3_7 = Frame(frame3)
        frame3_7.grid(sticky=W)
        self.display = BooleanVar()
        cbtDisplay = Checkbutton(frame3_7, text='Display Reconstructions', variable=self.display).grid()
        self.display.set(True)

        frame3_8 = Frame(frame3, width=50)
        frame3_8.grid()
        btStart = Button(frame3_8, text='START RECONSTRUCTION', command=self.runRecon)
        btStart.grid(padx=30)
        Button.config(btStart, font=('Helvetica', '11'))
        btSave = Button(frame3_8, text='SAVE', command=self.saveRecon)
        btSave.grid(row=0, column=1, padx=30, sticky=NS)
        # btSave.place()
        Button.config(btSave, font=('Helvetica', '11'))

        #####################    Text  Frames   ###############################
        print(frame1.winfo_width())
        frameT1 = Frame(tabKES, height=9, width=47)
        # frameT1.grid(row=2, column=0, sticky=S)
        frameT1.pack()
        sbText = Scrollbar(frameT1)
        self.text = Text(frameT1, height=9, width=72, yscrollcommand=sbText.set,
                         relief=SUNKEN)
        sbText.config(command=self.text.yview)
        self.text.grid(row=0, column=0, sticky=S)
        sbText.grid(row=0, column=1, sticky=NS)

        frameT2 = Frame(tabRecon, height=9, width=47)
        frameT2.grid(row=1,  column=0, sticky=S)
        sbText = Scrollbar(frameT2)
        self.text = Text(frameT2, height=9, width=47, yscrollcommand=sbText.set,
                         relief=SUNKEN)
        sbText.config(command=self.text.yview)
        self.text.grid(row=0, column=0, sticky=S)
        sbText.grid(row=0, column=1, sticky=NS)

        ####################   Canvas Frame    ##############################
        # self.loaded = BooleanVar()
        self.frameCanvas = LabelFrame(tabRecon,bd=4,relief=GROOVE,
                            text = "Display",labelanchor=N)
        self.frameCanvas.grid(row=0, rowspan=3, column=1,padx=7)

        # display an empty plot on canvas
        self.figure = Figure(figsize=(4, 4))
        figure = FigureCanvasTkAgg(self.figure, master=self.frameCanvas)
        figure.draw()
        figure.get_tk_widget().grid()

        # ######################  Exit button   ################################
        btExit = Button(window, text="EXIT", fg="red", command=quit, height=1, width=4,
                        relief=FLAT, cursor='sailboat')
        btExit.grid(row=0, column=0, sticky=E+N,padx=5,pady=19)

        # photo = PhotoImage(master=canvas)
        # canvas.create_image(image=photo)

        ####################  change theme config   ##########################
        # # iterate through all the widgets
        # color = 'floral white'
        # # master.config(bg = color)
        # for widget in master.winfo_children():
        #     widget.grid(padx=5)
        #     if not widget.winfo_class() in ['Entry', 'Text']:
        #         widget.configure(bg=color, takefocus=True)
        #     for sub_widget in widget.winfo_children():
        #         if not sub_widget.winfo_class() in ['Entry', 'Text']:
        #             sub_widget.configure(bg=color, takefocus=True)
        #         for sub_sub_widget in sub_widget.winfo_children():
        #             if not sub_sub_widget.winfo_class() in ['Entry', 'Text', 'TCombobox']:
        #                 sub_sub_widget.configure(bg=color, takefocus=True)
        # btRun['bg'] = 'purple4'
        s = ttk.Style()
        s.configure('TNotebook',font='helvetica 11',padding=12)
        s.configure('TNotebook.Tab',padding=[141,5],font='helvetica 11')
        master.add(tabKES, text='Spectral Imaging')
        master.add(tabRecon, text='Reconstruction')

        master.mainloop()

    ###################  Command Functions   #################################
    def reconState(self):
        self.rbtRecon1['state'] = NORMAL if self.do_recon.get() else DISABLED
        self.rbtRecon2['state'] = NORMAL if self.do_recon.get() else DISABLED
        self.entryCenter['state'] = NORMAL if self.do_recon.get() else DISABLED
        if self.do_recon.get():
            pass
        else:
            self.recon.set(None)

    def sliceState(self):
        self.entryNproj['state'] = NORMAL if self.multislice.get() else DISABLED
        self.entrySlice['state'] = NORMAL if self.multislice.get() else DISABLED

    def sideWidthState(self):
        self.entrySideWidth['state'] = NORMAL if self.ct.get() else DISABLED

    def erangeState(self):
        if self.e_range.get():
            self.entryElow['state'] = NORMAL
            self.entryEhigh['state'] = NORMAL
        else:
            self.entryElow['state'] = DISABLED
            self.entryEhigh['state'] = DISABLED

    def processMurho(self):
        murho = mphy.murho(self.name.get(), 12.658)
        print("murho " + str(murho))

    def browseData(self):
        self.curr_path = choose_path()
        self.path.set(self.curr_path)
        self.save_path.set(self.curr_path + r'\Save')
        print(self.path.get())
        self.text.insert(END, self.curr_path + '\n')

    def browseSave(self):
        self.curr_path = choose_path()
        self.save_path.set(self.curr_path)
        print(self.save_path.get())

    def run(self):
        def thread_run():
            data_path = self.path.get()
            save_path = self.save_path.get()
            n_proj = self.nproj.get()
            algorithm = self.algorithm.get()
            multislice = self.multislice.get()
            slice = self.slice.get()
            ct = self.ct.get()
            side_width = self.side_width.get()
            if self.e_range.get():
                energy_range = [self.e_low.get(), self.e_high.get()]
            else:
                energy_range = 0
            lowpass = self.lowpass.get()
            use_torch = self.use_torch.get()
            use_file = self.use_file.get()
            fix_vertical_motion = self.fix_vertical_motion.get()
            if self.recon.get() == 'None':
                reconstruction = None
            else:
                reconstruction = self.recon.get()
            ct_center = self.center.get()
            snr = self.snr.get()
            _ = nei(data_path=data_path, save_path=save_path, n_proj=n_proj, algorithm=algorithm,
                    multislice=multislice, slice=slice, ct=ct, side_width=side_width,
                    e_range=energy_range, lowpass=lowpass, use_torch=use_torch, use_file=use_file,
                    fix_vertical_motion=fix_vertical_motion, reconstruction=reconstruction,
                    ct_center=ct_center, snr=snr)
            self.text.insert(END, 'NEI finished.\n')

        # multithreading. Prevent the program from frozen
        threading.Thread(target=thread_run).start()

    def AutoSave(self):
        Checkbutton.config(self.cbtAutoSave, bg='MediumPurple1' if self.auto_save.get() else 'gray70')
        if self.auto_save.get() and not self.recon_path.get():
            self.recon_path.set(choose_path())

    def browseSino(self):
        """
        Accepts data from '.pkl', numpy.ndarray, or image data
        :return:
        """
        filename = choose_file()
        if not filename == '':  # if something is choosen in the popup window for the save path of recons
            def thread_loadSino():
                self.sino_file = load_object(filename)
                self.text.insert(END, '\nLoaded:\n' + filename + '\n')
                # if self.sino_file is object("nei" structure), find the sino only.
                # Here the top module name is 'toolkit', because the 'save_object' function is in 'toolkit.py'
                if type(self.sino_file).__module__ == 'toolkit':
                    self.sino_file = self.sino_file.rho_t
                # if self.sino_file is from an image, pop up a warning for value change
                elif type(self.sino_file).__module__ == 'imageio.core.util':
                    self.sino_file = np.array(self.sino_file)
                    self.text.insert(END, '\nWarning:\nSinogram loaded from an IMAGE file. '
                                          r'Values are most likely not representing the true $\rho_t$.')
                # otherwise, only numpy.ndarray is supported
                elif not type(self.sino_file).__module__ == 'numpy':
                    self.text.insert(END, '\nError:\n'
                                          'Loaded Sinogram data type is NOT SUPPORTED.')
                    raise Exception('Loaded Sinogram data type is NOT SUPPORTED.')
                # use self.loaded as a switch for target sino and sino display
                # self.loaded.set(True)
                self.sino_file_shape = self.sino_file.shape
                self.num_sino = int(np.prod(np.array(self.sino_file_shape[:-2])))
                print('num_sino', self.num_sino)

                # use the number of dimensions before the last two to calculate the number of sinograms.
                # When the dimension is only two, np.prod(np.array([]))=1.0
                shape = self.sino_file_shape
                # The sinogram to reconstruct
                self.sino_array = self.sino_file.reshape(self.num_sino, shape[-2], shape[-1])
                # update the available values for target sinogram
                self.update_cbox = True
                self.cboxTarget.configure(state='readonly')
                self.btShowSino.configure(state=NORMAL)
                self.updateCbox()
                # display the first sinogram in loaded sinograms
                self.selectSino()
                self.text.insert(END, str(self.num_sino) + ' Sinograms Loaded\n')

            self.text.insert(END, 'Loading Sinograms\n')
            threading.Thread(target=thread_loadSino).start()
        else:  # do nothing
            pass

    def updateCbox(self):
        if self.update_cbox:  # if sinograms loaded, update the Combobox
            self.sino_index = ['All']
            self.sino_index.extend(list((np.arange(self.num_sino) + 1).astype(str)))
            print('sino_index', self.sino_index)
            self.cboxTarget.config(values=self.sino_index)
            self.cboxTarget.current(0)  # use the first element as the default in combobox
            print(self.cboxTarget.get())

    def selectSino(self):
        if self.update_cbox:  # Only when something has been loaded
            id = self.target_sino_id.get()
            if id == 'All':
                id = 1
            else:
                id = int(id)
            print('id', id)
            self.target_sino = self.sino_array[id - 1]
            #################  display self.target_sino  #################################
            # if target_id is 0, display the first one. (Recon for all)

            # prepare the figure to show
            self.figure = Figure(figsize=(4, 4))
            a = self.figure.add_subplot(1, 1, 1)
            a.imshow(self.target_sino)

            print('display target_sino')
            # clear the frameCanvas before displaying
            for child_widget in self.frameCanvas.winfo_children():
                child_widget.destroy()
            # display the self.figure on canvas
            figure = FigureCanvasTkAgg(self.figure, master=self.frameCanvas)
            figure.draw()
            figure.get_tk_widget().grid()

    def runRecon(self):

        def thread_runRecon():
            recon_funcs = {'idl': idl_recon, 'skimage': skimage_recon}
            ######### check how many recons need to be done
            targets = self.target_sino_id.get()
            if targets in ['All', '0']:
                # Run the recon. Note: convert the unit of pixel size to Centimeter
                self.recons = recon_funcs[self.reconFunc.get()](self.sino_file,
                                                                pixel_size=(self.pixel.get() / 10000),
                                                                center=self.rotCenter.get())
            else:
                self.recons = recon_funcs[self.reconFunc.get()](self.target_sino,
                                                                pixel_size=(self.pixel.get() / 10000),
                                                                center=self.rotCenter.get())
            ######### check whether to save or not
            if self.auto_save.get():
                save_recon(self.recon_path.get(), self.recons)

            ######### display reconstruction if needed
            def displayRecon(recon,counter):
                print(recon.shape)
                if recon.ndim >= 3:
                    for i in range(recon.shape[0]):
                        counter+=1  # use counter to name recon windows
                        displayRecon(recon[i],counter)
                else:

                    self.windowRecon = Toplevel()
                    self.windowRecon.title('RECON '+str(counter))
                    figure_recon = Figure(figsize=(5, 5))
                    a = figure_recon.add_subplot(1, 1, 1)
                    a.imshow(recon, cmap='gray_r')
                    # display the figure_recon on canvas
                    figure = FigureCanvasTkAgg(figure_recon, master=self.windowRecon)
                    figure.draw()
                    figure.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
                    # display toolbar
                    toolbar = NavigationToolbar2Tk(figure, self.windowRecon)
                    toolbar.update()
                    figure._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

                    print('end')
            if self.display.get():
                displayRecon(self.recons,0)
            self.text.insert(END, '\nReconstruction finished\n')
        self.text.insert(END,'\nReconstruction started\n')
        threading.Thread(target=thread_runRecon).start()

    def browseReconPath(self):
        self.recon_path.set(choose_path())

    def saveRecon(self):
        # save when there is path and recon
        if not self.recon_path.get():  # if 'path' is empty, choose path.
            self.recon_path.set(choose_path())
        if self.recon_path.get() and self.recons:  # if 'recons' is not empty, then we can save recons
            save_recon(self.recon_path.get(), self.recons)

    def test(self):
        print('good')


NearEdgeImaging()
