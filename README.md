# Sales pitch

\- Ever felt the pain of transferring files to your peers?

\- Yeah, well we've got Facebook and email to transfer them.

\- What if you file is bigger than 25MB? What if you want to transfer a 10GB archive or a VM image?

Online file sharing services are cool, however, there are 2 things I dislike about them:
1. Sending any file to a peer means uploading it on a server first and then my peer has to download it which is a total waste of traffic. What if my bandwidth is low?
2. Privacy concerns - I don't want someone potentially snooping on my files.

Peer-to-peer should be easy, especially when connected to the same network! How do we do it then?

Read on.

# What is this project about?
`pysync` is an application that simplifies file transfers between peers connected to the same network.

It is a wrapper around the popular [rsync](https://en.wikipedia.org/wiki/Rsync) tool.
[The way rsync works](https://rsync.samba.org/how-rsync-works.html) is really clever and it's quite easy to synchronize files on different machines.

The issue is that 99% of the time rsync is used with ssh and having ssh access to someone's computer is not desirable (at least from their point of view).

Fortunately, you can use rsync with ssh by severely limiting the access you have over that channel.
To be more precise you are allowed only to run `rsync --server` on the receiving side.

# Demo

Here you can see a simple example. The client on the left wants to send `test.txt` to the client on the left. You can see that both machines have different ip addresses but are on the same network. Before running `pysync` the `rsync` command fails dues to missing permissions, but once the public key of the machine on the right is imported, rsync succeeds and the file is  successfully sent.

![](./pysync-demo.gif)

Currently key importing can be done in several ways with `-i` or `--import`:
- Raw string of passed
- Read from a file
- Github username

Note that for each of the last two, if multiple keys are found, they will all be added.

Now since you are importing other people's (hopefully ones you trust) keys it would be a good idea to limit the share directory in some way.
You don't want people trolling you by sending 100GB files just do troll you and leave with without any free space.

`pysync` to the help - you can run `pysync --size <some size>` to set a limit to how big the public directory may grow up to.

# TODO:
- smb support
# Dependencies

python3-libguestfs
