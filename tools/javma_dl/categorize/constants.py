"""Constants for article categorization."""

# Specialty categories and their keywords
SPECIALTIES = {
    # Main categories
    "Surgery": [
        "surgery", "surgical", "operation", "procedure", "postoperative",
        "preoperative", "intraoperative", "incision", "suture", "resection",
        "amputation", "graft", "implant", "reconstruction", "repair",
        "orthopedic", "bone", "joint", "fracture", "arthroscopy",
        "soft tissue", "laparoscopic", "thoracoscopic", "neurosurgery"
    ],
    
    # Internal Medicine subspecialties
    "Internal Medicine": [
        "medical", "treatment", "therapy", "management", "medication",
        "disease", "disorder", "condition", "clinical", "therapeutic"
    ],
    "Cardiology": [
        "cardiac", "heart", "cardiovascular", "echocardiogram", "arrhythmia",
        "murmur", "valve", "pacemaker", "hypertension", "thrombosis"
    ],
    "Neurology": [
        "neurologic", "brain", "spinal", "seizure", "neuropathy",
        "encephalopathy", "myelopathy", "paralysis", "ataxia", "vestibular"
    ],
    "Oncology": [
        "cancer", "tumor", "neoplasia", "chemotherapy", "oncologic",
        "radiation", "metastasis", "lymphoma", "sarcoma", "carcinoma"
    ],
    "Endocrinology": [
        "endocrine", "hormone", "thyroid", "diabetes", "adrenal",
        "pancreatic", "pituitary", "metabolic", "cushing", "addison"
    ],
    "Gastroenterology": [
        "gastrointestinal", "digestive", "intestinal", "hepatic", "pancreatic",
        "liver", "bowel", "stomach", "esophageal", "colitis"
    ],
    "Respiratory": [
        "respiratory", "pulmonary", "lung", "airway", "bronchial",
        "pneumonia", "asthma", "bronchitis", "pleural", "tracheal"
    ],
    "Infectious Disease": [
        "infection", "infectious", "bacterial", "viral", "fungal",
        "antibiotic", "antimicrobial", "pathogen", "resistance", "sepsis"
    ],
    "Nephrology": [
        "kidney", "renal", "urinary", "bladder", "urethra",
        "nephritis", "urolithiasis", "proteinuria", "azotemia", "dialysis"
    ],
    "Dermatology": [
        "skin", "dermal", "cutaneous", "allergy", "atopy",
        "pruritus", "lesion", "rash", "otitis", "dermatitis"
    ],
    "Immunology": [
        "immune", "immunologic", "allergy", "autoimmune", "hypersensitivity",
        "vaccination", "antibody", "immunotherapy", "immunosuppression"
    ]
}

# Status codes for file suffixes
STATUS_CODES = {
    'not_journal': 'nj',
    'not_small_animal': 'ns',
    'unclear_category': 'uc',
    'error': 'err'
}

# Maximum filename length
MAX_FILENAME_LENGTH = 100

# Category mapping for routing
SURGICAL_CATEGORIES = {
    "Surgery",  # All surgical articles go here
    "Orthopedic Surgery",
    "Soft Tissue Surgery",
    "Neurosurgery"
}

# Internal medicine categories for directory creation
INTERNAL_MEDICINE_CATEGORIES = {
    "Internal Medicine",
    "Cardiology",
    "Neurology", 
    "Oncology",
    "Endocrinology",
    "Gastroenterology",
    "Respiratory",
    "Infectious Disease",
    "Nephrology",
    "Dermatology",
    "Immunology"
}