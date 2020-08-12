import glob,os
import sys
import numpy as np
import cv2
from local_mmt import matchTemplates


def get_boxes(path):
    image_rg = cv2.imread(path)
    image_rgb = cv2.cvtColor(image_rg, cv2.COLOR_BGR2RGB)

    image_t = cv2.imread('templete_pt2.png')
    templete = image_t#[1450:1600,2250:2390]
    
    templete_rgb = cv2.cvtColor(templete, cv2.COLOR_BGR2RGB)
    listTemplate = [('temp', templete_rgb)]
    tubes = matchTemplates(listTemplate, image_rgb, N_object=8,score_threshold=0.2, method=cv2.TM_CCOEFF_NORMED, maxOverlap=0.3)

    return sorted(tubes)


def match_color(path,TC,boxes,img_path,img_names):
#     img_path,img_names = get_dir(path)
#     boxes = get_boxes(img_path[-1])

    final_diff = []
    img_path = img_path[-15:]
    img_names =img_names[-15:]
    diff = []
    for i,img in enumerate(img_path):
        raw_diff = []
        image = cv2.imread(img)
        image_rgb= cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_yuv = RGB2YUV(image_rgb)
  

        xt,yt,wt,ht = boxes[TC-1]
        templete_local = image_yuv[yt:yt+ht-150,xt:xt+wt]

        tY,tU,tV= cv2.split(templete_local)
        for box in boxes:
            x,y,w,h = box
            qurey_img = image_yuv[y:y+h-150,x:x+w]
   
            Y,U,V = cv2.split(qurey_img)
            diff_U = np.sum(np.abs( U -tU))

            diff_V = np.sum(np.abs(V - tV))

            diff_UV = diff_U + diff_V
  
            raw_diff.append(diff_UV/1000)

        final_diff.append([raw_diff,img_names[i]])
    return final_diff

def get_dir(directory):
    img_path = []
    img_names = []
    for path,subdirs,files in os.walk(directory):

        for name in files:
            if name.endswith('.png'):
                img_path.append(os.path.join(path,name))
                img_names.append(name.rsplit('.',-1)[0])
    return sorted(img_path),sorted(img_names)

def mov_mean(results,windowS):   
    results = np.asarray(results)

    window = windowS
    mv_avg_results = []
    for i in range(window,len(results)):
        t1_sum =0
        t2_sum = 0
        t3_sum = 0
        t4_sum = 0
        t5_sum = 0
        t6_sum = 0
        t7_sum = 0
        t8_sum = 0
        for j in range(i-window,i):
            t1_sum += results[j][0][0]
            t2_sum += results[j][0][1]
            t3_sum += results[j][0][2]
            t4_sum += results[j][0][3]
            t5_sum += results[j][0][4]
            t6_sum += results[j][0][5]
            t7_sum += results[j][0][6]
            t8_sum += results[j][0][7]
        name = results[i][1]
        mv_avg_results.append(([t1_sum/window,t2_sum/window,t3_sum/window,t4_sum/window,t5_sum/window,t6_sum/window,t7_sum/window,t8_sum/window],name))
#         print(([t1_sum/window,t2_sum/window,t3_sum/window,t4_sum/window,t5_sum/window,t6_sum/window,t7_sum/window,t8_sum/window],name))
    return mv_avg_results

def RGB2YUV( rgb ):
     
    m = np.array([[ 0.29900, -0.16874,  0.50000],
                 [0.58700, -0.33126, -0.41869],
                 [ 0.11400, 0.50000, -0.08131]])
     
    yuv = np.dot(rgb,m)
    yuv[:,:,1:]+=128.0
    return yuv

def check_dist(dist,red = 1):
    color_change = {
    'Test_tube1_NEG':0,
    'Test_tube2':0,
    'Test_tube3':0,
    'Test_tube4':0,
    'Test_tube5':0,
    'Test_tube6':0,
    'Test_tube7':0,
    'Test_tube8_POS':0}
        

    for i,(vs,k) in enumerate(dist):

      
        for j,(v,(test_tube,status)) in enumerate(zip(vs,color_change.items())):
    #         print(v)
    #         print("j:{}   v:{}".format(j,v))
            if (v >= 47) and red : #470
                color_change[test_tube] = 1
            
            if (v <= 47) and not red : ###500
                color_change[test_tube] = 1


    return ("{}.{}.{}.{}.{}.{}.{}.{}".format(color_change['Test_tube1_NEG'],color_change['Test_tube2'],color_change['Test_tube3'],color_change['Test_tube4'],color_change['Test_tube5'],color_change['Test_tube6'],color_change['Test_tube7'],color_change['Test_tube8_POS']))

def run_color_check(_dir,NTC,PTC):
    
    paths,names = get_dir(_dir)
    boxes = get_boxes(paths[-1])
    
    resutls = match_color(_dir,TC=NTC,boxes=boxes,img_path=paths,img_names=names)
    resutls_orange = match_color(_dir,TC=PTC,boxes=boxes,img_path=paths,img_names=names)
    orange = check_dist(mov_mean(resutls_orange,5),0)
#     print('Orange:{}'.format(orange))
    pink = check_dist(mov_mean(resutls,5),1)
#     print('Pink:{}'.format(pink))
    
    if pink == orange:
        return orange
    else :
        return '.4'

