from collections import defaultdict

semantic_cube = defaultdict(
    lambda: defaultdict(lambda: defaultdict(lambda: None)))

semantic_cube['int']['+']['int'] = 'int'
semantic_cube['int']['+']['float'] = 'float'
semantic_cube['float']['+']['int'] = 'float'
semantic_cube['float']['+']['float'] = 'float'

semantic_cube['int']['-']['int'] = 'int'
semantic_cube['int']['-']['float'] = 'float'
semantic_cube['float']['-']['int'] = 'float'
semantic_cube['float']['-']['float'] = 'float'

semantic_cube['int']['*']['int'] = 'int'
semantic_cube['int']['*']['float'] = 'float'
semantic_cube['float']['*']['int'] = 'float'
semantic_cube['float']['*']['float'] = 'float'

semantic_cube['int']['/']['int'] = 'int'
semantic_cube['int']['/']['float'] = 'float'
semantic_cube['float']['/']['int'] = 'float'
semantic_cube['float']['/']['float'] = 'float'

semantic_cube['int']['=']['int'] = 'int'
semantic_cube['float']['=']['int'] = 'float'
semantic_cube['float']['=']['float'] = 'float'
semantic_cube['char']['=']['char'] = 'char'

semantic_cube['int']['<']['int'] = 'bool'
semantic_cube['float']['<']['int'] = 'bool'
semantic_cube['int']['<']['float'] = 'bool'
semantic_cube['float']['<']['float'] = 'bool'

semantic_cube['int']['<=']['int'] = 'bool'
semantic_cube['float']['<=']['int'] = 'bool'
semantic_cube['int']['<=']['float'] = 'bool'
semantic_cube['float']['<=']['float'] = 'bool'

semantic_cube['int']['>']['int'] = 'bool'
semantic_cube['float']['>']['int'] = 'bool'
semantic_cube['int']['>']['float'] = 'bool'
semantic_cube['float']['>']['float'] = 'bool'

semantic_cube['int']['>=']['int'] = 'bool'
semantic_cube['float']['>=']['int'] = 'bool'
semantic_cube['int']['>=']['float'] = 'bool'
semantic_cube['float']['>=']['float'] = 'bool'

semantic_cube['int']['==']['int'] = 'bool'
semantic_cube['float']['==']['int'] = 'bool'
semantic_cube['int']['==']['float'] = 'bool'
semantic_cube['float']['==']['float'] = 'bool'
semantic_cube['char']['==']['char'] = 'bool'

semantic_cube['int']['<>']['int'] = 'bool'
semantic_cube['float']['<>']['int'] = 'bool'
semantic_cube['int']['<>']['float'] = 'bool'
semantic_cube['float']['<>']['float'] = 'bool'
semantic_cube['char']['<>']['char'] = 'bool'
