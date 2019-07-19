import os
import clr
clr.AddReference('System.Drawing')
apipath = os.path.join(os.getcwd(), "MPK_API.dll")
from MPK_API import *
from System.Drawing import *
from System import String

mpkapi = MPK_API()

# creating rectangle for subframe region
rect = Rectangle(0,0, 1000, 1000)

# InitializeCamera(cameraSerial as String, showFeedbackUI as Boolean)
# result = mpkapi.InitializeCamera("159185561", False, True)
sn = "159486608"
result = mpkapi.InitializeCamera(sn, False, True)
print(String.Format("Init Camera Result - ErrorCode: {0}", result['ErrorCode']))
