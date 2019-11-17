def create_tracker(name):
    if name == "dasiamrpn":
        from src.tracker.dasiamrpn import DaSiamRPNTracker
        return DaSiamRPNTracker()
    
    if name == "csrt":
        from src.tracker.csrt import CSRTTracker
        return CSRTTracker()
    
    raise Exception("Tracker \"%s\" does not exist." % name)
