using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Net;
using System.Net.Sockets;

namespace TestUI
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {

        public MainWindow()
        {
            InitializeComponent();
            TCPSocket client = new TCPSocket();

            Connect_Button.Click += delegate (object sender, RoutedEventArgs e) { Connect_Button_Click(sender, e, client); };
            Ping_Button.Click += delegate(object sender, RoutedEventArgs e) { Button_Click(sender, e, client,"Ping"); };
            IgnON_Button.Click += delegate (object sender, RoutedEventArgs e) { Button_Click(sender, e, client, "2"); };
            IgnOFF_Button.Click += delegate (object sender, RoutedEventArgs e) { Button_Click(sender, e, client, "3"); };
            ValOP_Button.Click += delegate (object sender, RoutedEventArgs e) { Button_Click(sender, e, client, "4"); };
            ValCL_Button.Click += delegate (object sender, RoutedEventArgs e) { Button_Click(sender, e, client, "5"); };
            Launch_Button.Click += delegate (object sender, RoutedEventArgs e) { Confirm_Button_Click(sender, e, client, "Launch", "1"); };
            Abort_Button.Click += delegate (object sender, RoutedEventArgs e) { Button_Click(sender, e, client, "a"); };
            Kill_Button.Click += delegate (object sender, RoutedEventArgs e) { Confirm_Button_Click(sender, e, client, "Kill the Server", "kill"); };

            //Message.Text = 

        }

        void Connect_Button_Click(object sender, RoutedEventArgs e, TCPSocket client)
        {
            MessageBox.Show("Are you sure you wish to Connect?", "Confirm", MessageBoxButton.YesNo, MessageBoxImage.Question);
            client.init();
            client.sendMessage("Hello");
        }

        void Confirm_Button_Click(object sender, RoutedEventArgs e, TCPSocket client, string message, string command)
        {
            MessageBoxResult result = MessageBox.Show("Are you sure you wish to " + message + "?", "Confirm", MessageBoxButton.YesNo, MessageBoxImage.Question);
            if (result == MessageBoxResult.Yes) { client.sendMessage(command); }
        }

        void Button_Click(object sender, RoutedEventArgs e, TCPSocket client, string command)
        {
            client.sendMessage(command);
        }


    }
    public class TCPSocket
    {
        private string address;
        private IPAddress ip;
        private Int32 Port;
        private TcpClient client;
        private NetworkStream stream;

        public void init()
        {
            address = "192.168.1.10";
            ip = IPAddress.Parse(address);
            Port = 8080;
            client = new TcpClient(address, Port);
            stream = client.GetStream();
        }
            
        public void sendMessage(string message)
        {
            Byte[] data = System.Text.Encoding.UTF8.GetBytes(message);
            stream.Write(data, 0, data.Length);
        }
        public string recvMessage()
        {
            Byte[] buffer = new Byte[1024];
            stream.Read(buffer, 0, buffer.Length);
            string message = System.Text.Encoding.UTF8.GetString(buffer);
            return message;
        }

    }


}
