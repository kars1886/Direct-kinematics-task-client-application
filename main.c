#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#define PORT    8088
#define NUM     6

struct payload
{
    uint64_t timestamp;
    double theta[NUM];
};


// Simple UDP server
int main() {
    // Output data
    double thetas[][NUM] = {
        {10.0, -50.0, -60.0, 90.0, 50.0, 0.0},
        {0.0, -90.0, 0.0, -90.0, 0.0, 0.0},
        {60.0, 60.0, 60.0, 60.0, 60.0, 60.0},
        {0.0, 0.0, 0.0, 0.0, 0.0, 0.0},
        {179.0, 223.0, -74.0, 35.0, 65.0, 0.0}
    };

    struct sockaddr_in servaddr;    // Server address
    struct sockaddr cliaddr;        // Client address

    int sock = socket(AF_INET, SOCK_DGRAM, 0);

    if (sock < 0)
    {
        perror("Can't create socket: ");
        return(1);
    }

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(PORT);

    if (bind(sock, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("Can't bind socket: ");
        return(1);
    }

    socklen_t len;
    len = sizeof(cliaddr);

    // Receive any combination of 3 symbols
    char buf[4];
    recvfrom(sock, buf, 3, 0, &cliaddr, &len);

    // Send 5 messages
    for (int i = 0; i < 5; i++)
    {
        struct payload pd = {.timestamp = i};
        for (int j = 0; j < NUM; j++)
        {
            pd.theta[j] = thetas[i][j];
        }
        sendto(sock, &pd, sizeof(pd), MSG_CONFIRM, (const struct sockaddr *) &cliaddr, len);
        printf("Message %i sent\n", i + 1);
    }

    close(sock);

    return 0;
}
