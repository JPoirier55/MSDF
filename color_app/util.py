from PIL import Image
from PIL import ImageDraw
from selenium import webdriver
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import json
import math
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from color_app.colors_json import colors

color_json = colors


def test(filename):
    im = Image.open(filename)
    im = im.convert('RGB')
    width, height = im.size
    return width,height


def plot(X, cluster_centers):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], marker='o')
    ax.scatter(cluster_centers[:, 0], cluster_centers[:, 1],
               cluster_centers[:, 2], marker='x', color='red',
               s=300, linewidth=5, zorder=10)
    plt.show()


def find_euc_dist(x,y):
    sum = 0
    if len(x) > 3:
        x = tuple(x[0:2])
    for i in range(len(x)):
        t = (y[i] - x[i]) ** 2
        sum += t
    ed = math.sqrt(sum)
    return ed


def create_key(colors):
    img = Image.new('RGB', (200,200))
    ImageDraw.Draw(img).text((0, 0), 'Hello world!', (255,255,255))
    img.save('sample-out.jpg')


def meanshift(data, quantile):
    print('meanshifting')
    t = []
    for tup in data:
        t.append([tup[0], tup[1], tup[2]])
    X = np.asarray(t)
    bandwidth = estimate_bandwidth(X, quantile=quantile, n_samples=len(data))
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(X)
    cluster_centers = ms.cluster_centers_
    return cluster_centers


def process_meanshift(filename, quantile):
    print('process meanshifting')
    im = Image.open(filename)
    im = im.convert('RGB')
    im = im.resize((im.size), Image.NEAREST)
    pix = im.load()
    width, height = im.size
    img = Image.new('RGB', (width, height))
    total_colors = []
    for x in range(width):
        for y in range(height):
            total_colors.append(pix[x, y])
    cluster_centers = meanshift(total_colors, quantile)
    print('cluster centers')
    for x in range(width):
        for y in range(height):
            min_rgb = (0, 0, 0)
            min_dist = 99999
            for cluster_center in cluster_centers:
                dist = find_euc_dist(pix[x,y], cluster_center)
                if dist < min_dist:
                    min_dist = dist
                    min_rgb = cluster_center
            img.putpixel((x, y), (int(min_rgb[0]), int(min_rgb[1]), int(min_rgb[2])))
    filename = filename.split("/")[-1]
    newfilename = "media/results/" + filename.split(".")[0] + "_meanshift." + filename.split(".")[1]
    print(newfilename)
    img.save(newfilename)
    return newfilename


def rgbconvert(color):
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))


def scrape():
    driver = webdriver.PhantomJS()
    color_dict = {}
    for i in range(1,6):
        driver.get('http://camelia.sk/dmc_' + str(i) + '.htm')
        content = driver.page_source
        soup = BeautifulSoup(content)
        rows = soup.findAll('tr')[6:-1]

        for row in rows:
            tds = row.findAll('td')
            number = tds[0].find('font').text
            name = tds[1].find('font').text
            color = tds[2]['bgcolor'].strip("#")
            rgb = rgbconvert(color)
            name_clean = "".join(name.split())
            color_dict[number] = {'name': name_clean,
                                  'number': number,
                                  'color': color,
                                  'rgb': rgb}
            number = tds[3].find('font').text
            name = tds[4].find('font').text
            color = tds[5]['bgcolor'].strip("#")
            name_clean = "".join(name.split())
            rgb = rgbconvert(color)
            color_dict[number] = {'name': name_clean,
                                  'number': number,
                                  'color': color,
                                  'rgb': rgb}

    print(json.dumps(color_dict))


def process_dmc(filename):
    im = Image.open(filename)
    im = im.convert('RGB')
    pix = im.load()
    width, height = im.size
    img = Image.new('RGB', (600,800), 'white')
    image_colors = {}
    colors = []
    dmc_colors = {}
    for x in range(width):
        for y in range(height):
            if pix[x, y] not in image_colors:
                dist_min = 99999
                min_rgb = (0, 0, 0)
                dmc_name = ''
                id = 0
                for key, value in list(color_json.items()):

                    dist = find_euc_dist(pix[x,y], tuple(value['rgb']))
                    if dist < dist_min:
                        dist_min = dist
                        dmc_name = value['name']
                        id = value['number']
                        min_rgb = value['rgb']
                img.putpixel((x+100, y+100), tuple(min_rgb))
                image_colors[pix[x,y]] = tuple(min_rgb)
                if tuple(min_rgb) not in colors:
                    colors.append(tuple(min_rgb))
                    dmc_colors[id] = {'name': dmc_name, 'rgb': tuple(min_rgb)}
            else:
                img.putpixel((x+100,y+100), image_colors[pix[x,y]])
    I1 = ImageDraw.Draw(img)
    I1.text((100,height+175), "Colors needed:", (0,0,0))
    text_space = 0
    for key, value in list(dmc_colors.items()):
        I1.ellipse((100, height+200+text_space, 115, height+200+text_space+15), fill=value['rgb'], outline=(125, 125, 125))
        I1.text((130,height+200+text_space), f"{key} - {value['name']}", (0,0,0))
        text_space += 20

    print(colors)
    print(dmc_colors)
    filename = filename.split("/")[-1]
    newfilename = "media/dmc_results/" + filename.split(".")[0] + "_dmc." + filename.split(".")[1]
    img.save(newfilename)
    return newfilename


if __name__ == '__main__':
    process_meanshift('base.png')
    process_dmc('base.png')

