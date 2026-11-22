"""Only the native core's existing git calls receive a process-local option."""
def install(core):
 original=core.git
 def git(root,*arguments):return original(root,'-c','core.longpaths=true',*arguments)
 core.git=git
 return {'original_callable':original,'process_local_option':'git -c core.longpaths=true','global_user_config_changed':False}
