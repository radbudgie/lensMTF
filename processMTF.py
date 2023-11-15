import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import glob
## fill this in to crawl a director
files = glob.glob(r"../../../Pictures/FUJIFILM/10-24 10mm/*.tif")

extract_window = 40
line_window = 32
pts_to_analyze = 5
output_file = "out_ref.csv"
def tellme(s):
    print(s)
    plt.title(s, fontsize=16)
    plt.draw()
output_summary = []
coords = []
for jj, filename in enumerate(files):
    print(filename)
    im = matplotlib.image.imread(filename).astype(float)
    im /= np.max(im.astype(float))
    im = im ** (2.2)
    if len(coords) == 0:
        plt.figure(figsize=(15,10))
        plt.imshow(im)
        plt.title(filename)
        while True:
            coords = plt.ginput(pts_to_analyze, timeout=-1, mouse_stop=None)
            coords_plt = np.array(coords)
            ps = plt.plot(coords_plt[:,0], coords_plt[:,1], 'r+')
            tellme("click if not OK?")
            if plt.waitforbuttonpress():
                break
            for p in ps:
                p.remove()
        plt.close()
        print(coords)
    MTFs = []
    for ii in range(pts_to_analyze):
        sub_im = im[
            int(coords[ii][1]-extract_window):int(coords[ii][1]+extract_window),
            int(coords[ii][0]-extract_window):int(coords[ii][0]+extract_window)
        ]
        plt.figure(1)
        plt.subplot(3,2,ii + 1)
        plt.imshow(sub_im)
        plt.colorbar()
        plt.xlim(0, 2 * extract_window)
        plt.ylim(0, 2 * extract_window)

        LSF_all = np.diff(sub_im.astype(float), axis=1)

        center = np.trapz(LSF_all*np.arange(LSF_all.shape[1]), axis=1) / np.trapz(LSF_all, axis=1)
        edge_f = np.poly1d(np.polyfit(np.arange(LSF_all.shape[0]), center + 0.5, deg=1))
        ys = np.arange(LSF_all.shape[0])
        plt.plot(edge_f(ys), ys, 'r')

        composite_edge = []
        for y in ys:
            x = np.linspace(edge_f(y)-(line_window)/2, edge_f(y)+(line_window)/2, line_window*16+1)
            edge = np.interp(x, ys, sub_im[y, :])
            composite_edge.append(edge)
        composite_edge = np.array(composite_edge)
        EF = np.average(composite_edge, axis=0)
        ESF = np.diff(EF)
        MTF = np.abs(np.fft.fftshift(np.fft.fft(ESF)))
        MTF/=np.nanmax(MTF)
        f = np.fft.fftshift(np.fft.fftfreq(len(MTF), 1 / 16))
        plt.figure(2)
        plt.plot(f, MTF, label=f"{ii}")
        plt.xlim(0, 1)
        print(np.interp([1/6, 0.25, 0.5], f, MTF))
        MTFs.append(np.interp([1/6, 0.25, 0.5], f, MTF))
                    
    for ii in range(pts_to_analyze):
        output_summary.append(
            {
                "filename": filename,
                "MTF0.25": MTFs[ii][1],
                "MTF0.5": MTFs[ii][2],
                "x_coord": coords[ii][0],
                "y_coord": coords[ii][1],
                "index": ii,
                
            }
        )
    plt.figure(1)
    plt.tight_layout()


    plt.waitforbuttonpress()
    plt.figure(1)
    plt.close()
    plt.figure(2)
    plt.close()
df_summary = pd.DataFrame(output_summary)
df_summary.to_csv(output_file)