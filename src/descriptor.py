def compile_descriptor(c,m):
 if not m["mapping_found"]: return None
 return {"service_type":c["service_type"],"service_profile":{k:c.get(k) for k in ["latency_ms","bandwidth_mbps","reliability","device_count","coverage","objective"]},"standards_mapping":m}