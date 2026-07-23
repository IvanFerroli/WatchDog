# Distribuição Windows

## Artefato para o usuário

Envie somente `AlwaysTrackWatchdog-<versão>-Setup.exe`, disponível em
`dist/installer/`. O computador de destino não precisa de Python, PowerShell,
WSL, Git ou uma cópia do repositório.

O instalador é per-user, não solicita privilégio administrativo e instala em
`%LOCALAPPDATA%\Programs\AlwaysTrack\Watchdog`. Ele cria atalhos no Menu Iniciar
e na Área de Trabalho. Ambos apontam diretamente para
`AlwaysTrackWatchdog.exe` e usam o ícone AlwaysTrack embutido.

Na instalação, a opção **Iniciar o AlwaysTrack Watchdog com o Windows** fica
desmarcada por padrão. Quando selecionada, o instalador cria um atalho do mesmo
executável na pasta de inicialização do usuário. Reexecutar o Setup permite
alterar essa opção.

## Instalar ou atualizar

1. Feche o AlwaysTrack Watchdog se ele estiver aberto.
2. Execute `AlwaysTrackWatchdog-<versão>-Setup.exe`.
3. Mantenha ou altere a opção de autostart.
4. Conclua o assistente e inicie o aplicativo.

Uma atualização usa o mesmo `AppId`, substitui somente os binários e preserva
configuração, banco e logs em `%LOCALAPPDATA%\AlwaysTrack\Watchdog`.

O MVP ainda não possui assinatura Authenticode. O Windows SmartScreen pode
mostrar um aviso de editor desconhecido; confira a origem e o SHA-256 publicado
em `SHA256SUMS.txt` antes de prosseguir.

## Build do release

Em Windows com Python 3.12 e Inno Setup 6:

```powershell
./scripts/build_windows.ps1 -SmokeInstaller
```

O script usa um ambiente Python temporário, executa qualidade e testes, gera o
bundle PyInstaller, compila o Setup, valida instalação/atalhos/autostart e
desinstala o smoke. O resultado transferível e seu manifesto SHA-256 ficam em
`dist/installer/`.

Não distribua `scripts/run_watchdog_windows.ps1`: ele é apenas um launcher de
desenvolvimento e depende de um ambiente Python local.
