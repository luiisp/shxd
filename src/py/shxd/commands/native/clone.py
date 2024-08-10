
import requests
import base64
import itertools
import re
import sys
from ...utils import Colors
from git import Repo
import os

exclude_backlist = [
    "bash", "shell","console", "powershell", "cmd", "terminal", "console", "prompt", "command", "line", "cli", "js", "py", "html", "script"
]
install_steps_keywords = [
    "Instalação", "Installing","Installation","Setup", "Install", "Setup", "Setup", "Running", "Rodando", "Run","Deployment"
]   


def extract_between_markers(txt:str) -> list:
    pattern = r'```(.*?)```|`(.*?)`'
    matches = re.findall(pattern, txt, re.DOTALL)
    results = []
    for match in matches:
        resultado = match[0] if match[0] else match[1]

        results.append(resultado.strip())
        
    return results


def get_suggestions(owner: str, repo: str):
    api_url = f'https://api.github.com/repos/{owner}/{repo}/readme'
    response = requests.get(api_url)

    if response.status_code == 200:
        readme_content = base64.b64decode(response.json()['content']).decode('utf-8')
        after_installation = None
        for keyword in install_steps_keywords:
            if keyword in readme_content:
                after_installation = readme_content.split(keyword)[1]
                resultados = extract_between_markers(after_installation)

                resultados_separados = [bloco.split('\n') for bloco in resultados if len(bloco) > 0]
                url = ''
                results = list(itertools.chain(*resultados_separados))
                filtered_results = []

                next_continue = False # skip next item in loop
                for item in results:
                    if next_continue:
                        next_continue = False
                        continue

                    if item not in exclude_backlist:
                        if item.startswith('$ '):
                            item = item[2:]
                        if item.startswith('git clone'): 
                            # Skip 'cd' command if it's right after 'git clone'
                            if results and results[results.index(item) + 1].startswith('cd'):
                                next_continue = True 
                                continue
                            continue
                        if item.startswith('http://') or item.startswith('https://'):
                            url = item
                            continue
                        if item.startswith('/'):
                            continue
                        filtered_results.append(item)

                return filtered_results
    else:
        return None
    
def full_repo_size(path: str):

    def readable_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    return readable_size(total_size)


def local_clone(url:str,repo_name:str='repository'):
    err = None
    repo = None
    infos = {}
    try:
        repo = Repo.clone_from(url, repo_name)
        local_repo_path = repo.working_dir
        infos['statistic'] = {
            'total_size': full_repo_size(local_repo_path)

        }

    except Exception as e:
        if e.stderr:
            err = e.stderr.split('stderr:')[1]
        else:
            err = e 

    return {'infos': infos, 'err': err}


def clone(url:str):
    owner, repo = url.strip().split('/')[-2:]
    readme_install_sugesstions = get_suggestions(owner, repo)
    exe_precmds = False
    if readme_install_sugesstions:
        sys.stdout.write(f"""\n 🌐 {Colors().cyan}{owner}{Colors().reset}, the owner of this repository, recommended that you use the commands below to run the project:\n\n""")
        for i, suggestion in enumerate(readme_install_sugesstions, start=1):
            sys.stdout.write(f'  {Colors().cyan}{i}{Colors().reset}. {suggestion} \n')

        sys.stdout.write(f'\n    If you accept the execution, shxd will execute all the above commands sequentially automatically')
        sys.stdout.write(f'\n{Colors().red} 🛑 Before executing commands from strangers, ensure that they are safe and cannot damage your machine.{Colors().reset}')
        sys.stdout.write(f'\n{Colors().yellow} ⚠️ Do you really allow shxd to execute all these commands sequentially automatically?{Colors().reset} (Y/N): ')
        sys.stdout.flush()
        entry = sys.stdin.readline().strip()  
    
        if entry.lower() in ['y', 'yes']:
            exe_precmds = True

    sys.stdout.write(f'\n ⏳ Cloning Repository...')
    res = local_clone(url, repo_name=repo)
    if res['err'] is None:
        sys.stdout.write(f"\n{Colors().green} 📦 Repository cloned successfully! ({res['infos']['statistic']['total_size']}) {Colors().reset}")
        sys.stdout.write(f'\n    To revert the clone by deleting it from your machine, use the command "sx clone revert" {Colors().reset}')
        if exe_precmds:
            sys.stdout.write(f"""\n 🌐 {Colors().cyan} Starting execution of commands recommended by the owner: {Colors().reset}""")
            for i, cmd in enumerate(readme_install_sugesstions):
                sys.stdout.write(f'\n\n  {Colors().cyan}{i+1}{Colors().reset}. {cmd} \n\n')
                sys.stdout.flush()
                try:
                    os.system(f"cd {repo} &&" + cmd)
                except Exception as e:
                    sys.stdout.write(f'{Colors().red} 💢 Failed to execute command: {cmd} {Colors().reset}\n')
                    sys.exit(1)            
    else:
        sys.stdout.write(f'\n\n{Colors().red} 💢 Failed to clone repository: {res["err"]} {Colors().reset}\n')
        sys.exit(1)