MAP={x:{"threegpp":"network-slice service profile","oran":"RAN slice/A1 policy candidate"} for x in ["eMBB","URLLC","mMTC"]}
def map_standards(c):
 m=MAP.get(c.get("service_type")); return {"mapping_found":m is not None,"mapping":m,"profile":"3GPP Rel-18 + O-RAN R004"}