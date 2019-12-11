#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
#  Ctrl + Alt + L - форматирование кода
#
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def send_history(self):
        for msg in self.factory.history[-10::]:
            self.sendLine(msg.encode())

    def connectionMade(self):
        # Потенциальный баг для внимательных =)
        self.factory.clients.append(self)
        print(f"Users connected: {len(self.factory.clients)}")

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)
        print(f"Users connected: {len(self.factory.clients)}")

    def lineReceived(self, line: bytes):
        content = line.decode(encoding="utf-8", errors="ignore")

        if self.login is not None:
            content = f"Message from {self.login}: {content}"
            self.factory.history.append(content)
            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:
            # login:admin -> admin
            if content.startswith("login:"):
                self.login = content.replace("login:", "")
                if self.factory.logins:
                    if self.login in self.factory.logins:
                        self.sendLine(f"Login {self.login} is busy! Try another login.".encode())
                        self.login = None
                    else:
                        self.factory.logins.append(self.login)
                        self.sendLine("Welcome!".encode())
                        self.send_history()
                else:
                    self.factory.logins.append(self.login)
                    self.sendLine("Welcome!".encode())
            else:
                self.sendLine("Invalid login".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    history: list
    logins: list

    def startFactory(self):
        self.clients = []
        self.history = []
        self.logins = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
