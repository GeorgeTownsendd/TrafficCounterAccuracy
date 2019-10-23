import requests
import datetime
import subprocess
import time
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os


#USE 640
example_camera_url = 'https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00002.00{}.mp4'

def download_camera_video(foldername, camera, name='time'):
    if name == 'time':
        name = foldername  + str(datetime.datetime.now()) + '.mp4'
    video_download = requests.get(example_camera_url.format(camera))

    with open(foldername + name, 'wb') as f:
        for chunk in video_download.iter_content(chunk_size=256):
            f.write(chunk)

    print('Downloaded. Saved as {}'.format(name))
    return name

def show_video(file):
    start_time = time.time()
    print('loading {}'.format(file))
    '''
    show_video_process = subprocess.Popen(["vlc", file], stdout=subprocess.PIPE)
    start_time = time.time()
    print('Opening {}... Count cars traveling down the screen.')
    down_cars = int(input('Cars: '))
    end_time = time.time()
    run_time = end_time - start_time
    '''
    start_time = time.time()
    video_window = cv2.VideoCapture(file)
    ret, frame = video_window.read()
    counter = 0
    while True:
        ret, frame = video_window.read()
        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or ret==False:
            video_window.release()
            cv2.destroyAllWindows()
            end_time = time.time()
            break

        cv2.imshow('frame', frame)
        time.sleep(1/25)

    run_time = end_time - start_time
    #down_cars = 3#int(input('Cars: '))
    #print('Counted {} vehciles in {} seconds'.format(down_cars, run_time))

    return run_time


def load_database(foldername, directory=''):
    if directory == '':
        foldername = os.path.realpath(__file__).rsplit('/', 1)[0] + '/' + foldername + '/'
    else:
        foldername = directory + foldername

    contents = [f for f in os.listdir(foldername) if os.path.isfile(foldername + f)]
    print('[INFO] Loaded {} items from {}'.format(len(contents), foldername))
    #print(contents)
    return [foldername, contents]


def run_video_analyser(process):
    print('[SUBINFO] ' + str(process))
    sub = subprocess.Popen(process,cwd=r'/home/george/Documents/Documents/School/Science Extension/Major Project/Manual Counter/',stdout=subprocess.PIPE, shell=True)
    while True:
        line = sub.stdout.readline().rstrip()
        if not line:
            break
        yield line

def analyse_video(folder, name):
    print('[SUBINFO] Starting object detection on {}'.format(name))
    folder = folder.rsplit('/', 2)[-2]
    folder += '/'
    process = 'python python-traffic-counter-with-yolo-and-sort/main.py --input {} --output {}.avi --yolo python-traffic-counter-with-yolo-and-sort/yolo-coco/'.format(folder + name, folder + 'output/{}'.format(name))
    #print(process)
    for line in run_video_analyser(process):
        pass
    if '.' in name:
        name = name[:name.index('.')]
    print(name)
    try:
        with open(folder + 'output/' + name + 'results.txt', 'r') as f:
            return int(f.readline())
    except FileNotFoundError:
        print('file not found: {}'.format(folder + 'output/' + name + 'results.txt'))
        return -1


def create_database(name, camera=640, n=2, directory = '',line=''):
    print('Creating database: {}...'.format(name))
    print('SIZE: {}\tCAMERA: {}'.format(n, str(camera)))
    if directory == '':
        foldername = os.path.realpath(__file__).rsplit('/', 1)[0] + '/' + name + '/'
    else:
        foldername = directory + name + '/'

    try:
        os.mkdir(foldername)
    except FileExistsError:
        print('Error! File {} already exists'.format(foldername))

    try:
        os.mkdir(foldername + 'output/')
        with open(foldername + 'output/config', 'w') as f:
            if line == '':
                f.write('(enter two comma seperated x,y coordinates on new lines')
            else:
                for coordinate in line:
                    f.write('{},{}\n'.format(coordinate[0], coordinate[1]))
    except:
        pass

    with open(foldername + '{}.txt'.format(name), 'w') as datafile:
        datafile.write('Original Name: {}\n'.format(name))
        datafile.write('Created: {}\n'.format(datetime.datetime.now()))

        for vid in range(n):
            vid += 1
            if vid == 1:
                pass
            else:
                time.sleep(305)
            download_camera_video(foldername, camera, name=str(vid))
            print('Video {}/{} downloaded. Waiting...\n'.format(vid, n))
            datafile.write('{},{}\n'.format(vid, datetime.datetime.now()))

    print('Database successfully created.')

def analyse_database(database, end=-1, start=-1):
    starttime = datetime.datetime.now()
    if end != -1:
        database[1] = database[1][:end]
    if start != -1:
        database[1] = database[1][start:]
    print('[INFO] Analysing {}'.format(database[0].rsplit('/', 2)[1]))
    results = []
    for n, video in enumerate([x for x in database[1] if x[-4:] != '.txt']):
        cars = analyse_video(database[0], video)
        results.append(cars)
        print('({}/{}) - {} cars in {}'.format(n, len(database[1]), cars, video))
    endtime = datetime.datetime.now()
    print('Runtime: {}'.format(endtime-starttime))
    return results


def get_results(foldername, directory = ''):
    if directory == '':
        foldername = os.path.realpath(__file__).rsplit('/', 1)[0] + '/' + foldername + '/output/'
    else:
        foldername = directory + foldername + '/output/'

    contents = [f for f in os.listdir(foldername) if os.path.isfile(foldername + f)]

    resultfiles = [x for x in contents if x[-4:] == '.txt']
    print('[INFO] Loaded {} results from {}'.format(len(resultfiles), foldername))
    resultnumbers = []
    for file in resultfiles:
        with open(foldername + file, 'r') as f:
            number = f.readline()
            resultnumbers.append(int(number))
    return resultnumbers

def load_manual_results(foldername, directory = ''):
    if directory == '':
        foldername = os.path.realpath(__file__).rsplit('/', 1)[0] + '/' + foldername + '/'
    else:
        foldername = directory + foldername + '/'

    contents = sorted([f for f in os.listdir(foldername) if os.path.isfile(foldername + f)])
    print('[INFO] Loaded {} manual reviews from {}'.format(len(contents), foldername))
    databases = {}
    for file in contents:
        database = int(''.join([x for x in file.split('-')[0] if x.isdigit()]))
        dataresults = []
        with open(foldername + file) as f:
            for result in f.readlines():
                #print(result)
                try:
                    dataresults.append(int(''.join([x for x in result.split(',')[1] if x.isdigit()])))
                except IndexError:
                    pass
        if database in databases.keys():
            databases[database].append(dataresults)
            for item in databases[database]:
                print('database {}: len {}'.format(database, len(item)))
        else:
            databases[database] = [dataresults]
    for key in sorted(databases.keys()):
        print('Loaded {} manual review files from database {}'.format(len(databases[key]), key))

    for database in databases.keys():
        databases[database] = [max(set(counts), key=counts.count) for counts in zip(*databases[database])] #returns the minimum mode of each item in the database e.g. [22, 33, 11, 22, 11] returns 11

    return databases


def graph_databases(manual_count, automatic_count, databases, title = 'Title', sorting='total'):
    n_groups = len(databases)
    #print(n_groups)
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8
    manres = []
    autres = []
    for x, data in enumerate(automatic_count):
        #print(x)
        if x + 1 in databases:
            autres.append(data)
    for database in manual_count.keys():
        if database in databases:
            #print(x[1])
            manres.append(manual_count[database])


    autres = [sum(data) for data in autres]
    manres = [sum(data) for data in manres]

    for d in manres:
        print(d)

    if sorting == 'reldifleft':
        rel_differences = [(man/aut) * 100 if aut != 0 else 99999 for man, aut in zip(manres, autres)]
        print(rel_differences)
        data = [[database, man, aut, rel] for database, man, aut, rel in zip(databases, manres, autres, rel_differences)]
        data = sorted(data, key = lambda x : x[3])

        databases = [x[0] for x in data]
        manres = [x[1] for x in data]
        autres = [x[2] for x in data]
        rel_differences = [x[3] for x in data]
        print(sorted(rel_differences))

    rects1 = plt.bar(index, manres, bar_width, alpha = opacity, color='b', label = 'Manual Count')
    rects2 = plt.bar(index + bar_width, autres, bar_width, alpha=opacity, color='g', label = 'Automatic Count')

    plt.xlabel('Database')
    plt.ylabel('Count')
    plt.title(title)
    plt.xticks(index+bar_width, databases)
    plt.legend()

    plt.tight_layout()
    plt.show()

def graph_time_progression(manual_count, automatic_count, databases):
    manres = []
    autres = []
    timestamps = load_timestamps(databases)
    for x, data in enumerate(automatic_count):
        # print(x)
        if x + 1 in databases:
            autres.append(data)
    for database in manual_count.keys():
        if database in databases:
            # print(x[1])
            manres.append(manual_count[database])

    database_rel_differences = []
    for n, database in enumerate(databases):
        for x, item in enumerate(manres[n]):
            try:
                if True:#item > 1 and autres[n][x] > 1:
                    database_rel_differences.append((item / autres[n][x]) * 100)
                else:
                    print(10 / 0)

            except ZeroDivisionError:
                database_rel_differences.append(9999999)
    print(timestamps)
    print(database_rel_differences)
    plt.xlim(0, 23)
    plt.ylim(0, 1000)
    plt.xlabel('Hour')
    plt.ylabel('Relative Difference (%)')
    plt.xticks([x for x in range(0, 24)])
    plt.scatter(timestamps, database_rel_differences)
    plt.title('Relative Difference by Time of Day')
    plt.show()



def load_timestamps(databases, directory = ''):
    if directory == '':
        foldername = os.path.realpath(__file__).rsplit('/', 1)[0] + '/'
    loaded = []
    for database in databases:
        with open(foldername + 'database_{}/database_{}.txt'.format(database, database), 'r') as f:
            for line in f.readlines():
                if ',' in line:
                    dateandtime = line.split(',')[1][:-1]
                    time = dateandtime.split(' ')[1]
                    hour = time.split(':')[0]
                    minute = time.split(':')[1]
                    loaded.append(((int(hour) - 9) % 24) + (int(minute) / 60)) #% 9 to convert to local UK time

    return loaded

def graph_timestamps(timestamps):
    n_groups = 24
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8
    print(timestamps)
    sums = [timestamps.count(n) for n in range(0, 24)]
    print(sums)

    rects1 = plt.bar(index, sums, bar_width, alpha=opacity, color='b')

    plt.xlabel('Hour')
    plt.ylabel('Source Videos')
    plt.title('Source Videos by Hour')
    plt.xticks(range(0, 24))
    plt.tight_layout()
    plt.show()

def t_test(man, res):
    n = len(man)
    man = np.array(man)
    res = np.array(res)
    var_man = man.var(ddof=1)
    var_res = res.var(ddof=1)

    s = np.sqrt((var_man + var_res)/2)

    t = (man.mean() - res.mean())/(s*np.sqrt(2/n))

    df = 2*n - 2

    p = 1 - stats.t.cdf(t,df=df)

    #print("t = " + str(t))
    #print("p = " + str(2 * p))
    ### You can see that after comparing the t statistic with the critical t value (computed internally) we get a good p value of 0.0005 and thus we reject the null hypothesis and thus it proves that the mean of the two distributions are different and statistically significant.

    ## Cross Checking with the internal scipy function
    t2, p2 = stats.ttest_ind(man, res)
    print('{} & {} & {} & {}'.format(round(np.std(man), 3), round(np.std(res), 3), round(t2, 3), round(p2, 3)))

autresults = [get_results('database_{}'.format(database)) for database in range(1, 24)]
manresults = load_manual_results('RESULTS')

#for t in range(1, 24):
#    relres = []
#    for n, database in enumerate(manresults.keys()):
#        if n + 1 == t:
#            # print(x[1])
#            for x, vid in enumerate(manresults[database]):
#                try:
#                    relres.append((vid / autresults[n][x]) * 100)
#                except ZeroDivisionError:
#                    pass

    #print(np.std(relres))
for t in range(0, 23):
    print('Database {}'.format(t+1))
    t_test(manresults[t+1], autresults[t])

#graph_databases(manresults,autresults, [18, 20, 23], title = 'Camera 628')

#x = load_timestamps([1,2 , 3, 4])
graph_time_progression(manresults, autresults, databases=[x for x in range(1, 24)])
