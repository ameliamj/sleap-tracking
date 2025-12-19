# cohorts
DYED_COHORTS = ['KL', 'EB', 'HF']
COLLAR_COHORTS = ['KL', 'EB', 'HF', 'KM', 'KF', 'NM', 'NF']

# directories
ROOTDIR = '/gpfs/radev/pi/saxena/aj764/'
TESTDIR = 'PairedTestingSessions/'
TRAINDIR = 'Training_COOPERATION/'
BYDIR = 'Training_COOP_1by1/'
LADIR = 'Training_LARGEARENA_Individual/'
JOBDIR = '/gpfs/radev/project/saxena/aj764/ood/projects/default/sleap_tracking'

# models (needs to be the WHOLE file path!!)
SINGLE = 'Tracking/DLC_SingleAnimal/SingleAnimal-V1-2024-07-16/SLEAP/models/240808_075503.single_instance.n=720'
CENTROID = {
    ('dyed', 'RG'): '',
    ('dyed', 'RB'): '',
    ('dyed', 'RY'): '',
    ('dyed', 'YB'): '',
    ('dyed', 'GY'): '',
    ('dyed', 'GB'): '',
    ('dyed', 'fiber pho'): '/gpfs/radev/pi/saxena/aj764/Nina_Model_Testing/Fiber/models/250723_170950.centroid',
    ('collar', 'RG'): '/gpfs/radev/pi/saxena/aj764/Nina_Model_Testing/Collars/Red-Green/models/250727_224035.centroid/',
    ('collar', 'RB'): '',
    ('collar', 'RY'): '',
    ('collar', 'YB'): '/gpfs/radev/pi/saxena/aj764/Nina_Model_Testing/Collars/Yellow-Blue/models/250729_222523.centroid/',
    ('collar', 'GY'): '',
    ('collar', 'GB'): ''
}
TOPDOWN = {
    ('dyed', 'RG'): '',
    ('dyed', 'RB'): '',
    ('dyed', 'RY'): '',
    ('dyed', 'YB'): '',
    ('dyed', 'GY'): '',
    ('dyed', 'GB'): '',
    ('dyed', 'fiber pho'): '/gpfs/radev/pi/saxena/aj764/Nina_Model_Testing/Fiber/models/250723_170950.multi_class_topdown',
    ('collar', 'RG'): '/gpfs/radev/pi/saxena/aj764/Nina_Model_Testing/Collars/Red-Green/models/250727_224035.multi_class_topdown/',
    ('collar', 'RB'): '',
    ('collar', 'RY'): '',
    ('collar', 'YB'): '/gpfs/radev/pi/saxena/aj764/Nina_Model_Testing/Collars/Yellow-Blue/models/250729_222523.multi_class_topdown/',
    ('collar', 'GY'): '',
    ('collar', 'GB'): ''
}

# MAGIC NUBMERS for error utils
# CHANGING MAX_VEL ON 8/15/2025 FROM 200 TO 100
MAX_VEL = 100 # 200 # pixels per frames that is max rat velocity
SMOOTHING = 10 # number of frames before and after nan value to use for smoothing
BAD_NAN = 0.20 # .30 # percent of initial nan at which point, don't consider correcting


# MAGIC NUMBERS for id utils
fps = 30 # frames per second the video was recorded at
# somewhat guessed numbers for the location of lever / mag
levx = 135
lev1y = 440
lev2y = 200
mag1y = 200
mag2y = 440
magx = 1280
MAXDIST = 100