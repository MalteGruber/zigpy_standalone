import asyncio
import aioconsole
_cmds=[]

def demo_command(*args, **kwargs):
    def inner(func):
        o={
        }
        o["commands"]=kwargs["commands"]
        o["desc"]=kwargs.get("desc","-")
        o["callback"]=func
        _cmds.append(o)
        return func
    return inner
 


def help():
    print("Avalible commands are")
    for cmd in _cmds:
        helpstr=""
        for c in cmd.get("commands"):
            helpstr+=f"{c} "
        helpstr=helpstr[:-1]

        print(f"{helpstr} \t: {cmd.get('desc')}")


async def _handle_command(argv):
    found=False
    if(argv in [["help"],["?"]]):
        help()          
        found=True 
            

    for cmd in _cmds:
        if argv[0] in cmd.get("commands"):
            callback=cmd.get("callback")
            await callback(argv)
            found=True
    if not found:
        help()

if __name__=="__main__":
    print("Do not run this file like this!")

async def tui_task():     
    try:   
        while True:
            line = await aioconsole.ainput('>')
            words=line.split(" ")
            
            try:
                await _handle_command(words)
            except Exception:
                import traceback
                print("Command error")
                traceback.print_exc()

    except Exception:
        import traceback
        traceback.print_exc()

tui_task_=None
def start_mincli():
    global tui_task_
    tui_task_= asyncio.create_task(tui_task())
def stop_minicli():
    tui_task_.cancel()
    print("")
