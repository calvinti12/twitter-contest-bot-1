# Print and log the text
def LogAndPrint(text):
    tmp = text.replace("\n", "")
    print(tmp)
    f_log = open('log', 'a')
    f_log.write(tmp + "\n")
    f_log.close()


def CheckError(r):
    r = r.json()
    if 'errors' in r:
        LogAndPrint("We got an error message: " + r['errors'][0]['message'] + " Code: " + str(r['errors'][0]['code']))
