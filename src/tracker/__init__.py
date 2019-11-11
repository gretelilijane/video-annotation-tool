def create_tracker(name):
    if name == "dasiamrpn":
        from src.tracker.dasiamrpn import DaSiamRPNTracker
        return DaSiamRPNTracker()
    
    raise Exception("Tracker \"%s\" does not exist." % name)
