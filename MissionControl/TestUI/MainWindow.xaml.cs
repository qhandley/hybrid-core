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
using System.Windows.Threading;
using System.Diagnostics;


namespace TestUI
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        TCPSocket client = new TCPSocket();
        string[] msgArray = new string[3];
        string lastMsg = "";
        Stopwatch stopWatch = new Stopwatch();

        public MainWindow()
        {
            InitializeComponent();
            client.connected = false;
            msgArray[0] = "";
            msgArray[1] = "";
            msgArray[2] = "";

            msg0.Text = msgArray[0];
            msg1.Text = msgArray[1];
            msg2.Text = msgArray[2];


            DispatcherTimer timer = new DispatcherTimer();
            timer.Interval = TimeSpan.FromSeconds(.02);
            timer.Tick += timer_Tick;
            

            Connect_Button.Click += delegate (object sender, RoutedEventArgs e) { Connect_Button_Click(sender, e, client, timer); };
            IgnTOG_Button.Click += delegate (object sender, RoutedEventArgs e) { Toggle_Button_Click(sender, e, client, "Ign"); };
            ValTOG_Button.Click += delegate (object sender, RoutedEventArgs e) { Toggle_Button_Click(sender, e, client, "Val"); };
            Launch_Button.Click += delegate (object sender, RoutedEventArgs e) { Confirm_Button_Click(sender, e, client, "Launch", "1"); };
            Abort_Button.Click += delegate (object sender, RoutedEventArgs e) { Button_Click(sender, e, client, "a"); };
            Kill_Button.Click += delegate (object sender, RoutedEventArgs e) { Confirm_Button_Click(sender, e, client, "Kill the Server", "kill"); };

            





        }

        private void timer_Tick(object sender, EventArgs e)
        {
            int numofMsg = 3;
            if (client.delay == false)
            {
                if (client.connected == true)
                {
                    Connect_Button.Background = Brushes.Green;
                    long startTime = stopWatch.ElapsedMilliseconds;
                    stopWatch.Start();
                    client.sendMessage("0");
                    string buffer = client.recvMessage();
                    stopWatch.Stop();
                    long timeDiff = stopWatch.ElapsedMilliseconds - startTime;
                    Latency.Text = timeDiff.ToString();
                    string[] temp = buffer.Split(';');
                    if (temp.Length > 1)
                    {
                        if (temp[0] != "0" && temp[0] != lastMsg)
                        {
                            for (int i = 0; i < numofMsg; i++)
                            {
                                if (msgArray[i] == "")
                                {
                                    msgArray[i] = temp[0];
                                    lastMsg = temp[0];
                                    break;
                                }
                                else if (msgArray[i] != "" && i == numofMsg - 1)
                                {
                                    for (int j = 0; j < numofMsg - 1; j++)
                                    {
                                        msgArray[j] = msgArray[j + 1];
                                    }
                                    msgArray[numofMsg - 1] = temp[0];
                                    lastMsg = temp[0];
                                }
                            }
                            msg0.Text = msgArray[0];
                            msg1.Text = msgArray[1];
                            msg2.Text = msgArray[2];
                            //msg4.Text = msgArray[4];
                        }
                        if (temp[1] == "1")
                        {
                            IgnTOG_Button.Background = Brushes.Green;
                            IgnTOG_Button.Content = "Ignition ON";
                        }
                        else
                        {
                            IgnTOG_Button.Background = Brushes.Red;
                            IgnTOG_Button.Content = "Ignition OFF";
                        }
                        if (temp[2] == "1")
                        {
                            ValTOG_Button.Background = Brushes.Green;
                            ValTOG_Button.Content = "Valve Open";

                        }
                        else
                        {
                            ValTOG_Button.Background = Brushes.Red;
                            ValTOG_Button.Content = "Valve Closed";
                        }
                        if (temp[3] == "1") { Burn.Text = "Burn Wire Connected"; }
                        else { Burn.Text = "Burn Wire Cut"; }
                        Pre.Text = temp[4];
                        Error.Text = temp[5];
                    }

                }
                else
                {
                    Connect_Button.Background = Brushes.LightGray;
                    IgnTOG_Button.Background = Brushes.LightGray;
                    ValTOG_Button.Background = Brushes.LightGray;
                    msgArray[0] = "";
                    msgArray[1] = "";
                    msgArray[2] = "";
                    msg0.Text = "";
                    msg1.Text = "";
                    msg2.Text = "";
                    Burn.Text = "";
                    Pre.Text = "";
                    Error.Text = "";
                    Latency.Text = "";
                }
            }
            else { client.delay = false; }
        }
        

        void Connect_Button_Click(object sender, RoutedEventArgs e, TCPSocket client, DispatcherTimer timer)
        {
            if (client.connected == false)
            {
                MessageBoxResult result = MessageBox.Show("Are you sure you wish to Connect?", "Confirm", MessageBoxButton.YesNo, MessageBoxImage.Question);
                if (result == MessageBoxResult.Yes)
                {
                    client.init();
                    if (client.connected == true)
                    {
                        client.sendMessage("Hello");
                        timer.Start();
                        MessageBox.Show("Connection Established", "Success", MessageBoxButton.OK, MessageBoxImage.Information);

                    }
                }
            }
            else
            {
                MessageBox.Show("Connection Already Established", "Information", MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }

        void Confirm_Button_Click(object sender, RoutedEventArgs e, TCPSocket client, string message, string command)
        {
            if (client.connected == true)
            {
                MessageBoxResult result = MessageBox.Show("Are you sure you wish to " + message + "?", "Confirm", MessageBoxButton.YesNo, MessageBoxImage.Question);
                if (result == MessageBoxResult.Yes) { client.sendMessage(command); }
            }
            else
            {
                MessageBox.Show("No Connection Established", "ERROR", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            
        }

        void Button_Click(object sender, RoutedEventArgs e, TCPSocket client, string command)
        {
            if (client.connected == true)
            {
                client.sendMessage(command);
            }
            else
            {
                MessageBox.Show("No Connection Established", "ERROR",MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
        void Toggle_Button_Click(object sender, RoutedEventArgs e, TCPSocket client, string command)
        {
            if (client.connected == true)
            {
                if(command == "Ign")
                {
                    if(IgnTOG_Button.Content.Equals("Ignition OFF"))
                    {
                        client.sendMessage("2");
                    }
                    else
                    {
                        client.sendMessage("3");
                    }
                }
                else if(command == "Val")
                {
                    if (ValTOG_Button.Content.Equals("Valve Closed"))
                    {
                        client.sendMessage("4");
                    }
                    else
                    {
                        client.sendMessage("5");
                    }
                }
            }
            else
            {
                MessageBox.Show("No Connection Established", "ERROR", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }


    }


    public class TCPSocket
    {
        public bool connected;
        public bool delay;
        private string address;
        private IPAddress ip;
        private Int32 Port;
        private TcpClient client;
        private NetworkStream stream;

        public void init()
        {
            if (connected == false)
            {
                address = "192.168.0.10";
                ip = IPAddress.Parse(address);
                Port = 8080;
                try { client = new TcpClient(address, Port); }
                catch (SocketException)
                {
                    MessageBox.Show("Connection Failed", "ERROR", MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }

                stream = client.GetStream();
                connected = true;
                delay = true;
            }
            
        }
        public void sendMessage(string message)
        {
            Byte[] data = System.Text.Encoding.UTF8.GetBytes(message);
            try { stream.Write(data, 0, data.Length); }
            catch (System.IO.IOException)
            {
                MessageBox.Show("Connection Failed", "Send ERROR", MessageBoxButton.OK, MessageBoxImage.Error);
                connected = false;
                //stream.Close();
            }
            if (message == "kill") {connected = false; }
        }
        public string recvMessage()
        {
            Byte[] buffer = new Byte[200];
            try { stream.Read(buffer, 0, buffer.Length); }
            catch (System.IO.IOException)
            {
                MessageBox.Show("Connection Failed", "Recieve ERROR", MessageBoxButton.OK, MessageBoxImage.Error);
                connected = false;
                //stream.Close();
                return "0";
            }
            string message = System.Text.Encoding.UTF8.GetString(buffer,0,200);
            return message;
        }

    }


}
