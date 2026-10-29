limitations (to my knowledge)


#not thread safe 
-concurrent calls may race when reading and updating request counts 

#memory cleanup
-inactive client keys are not automatically removed from internal dictionary 

#Fixed window boundary issue 
-requests can cluster around a window boundary

#Single Process storage
-requests counts are held in local memory and are not shared across multiple application instances 