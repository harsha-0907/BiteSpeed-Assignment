
from model import Contact, Request
from database import RedisDictionary
from typing import List
import time

def getTime():
    return int(time.time())

class Users:
    def __init__(self):
        self.users = RedisDictionary() # contactId: Contact
        self.emailMappings = {"": None} # email: contactId
        self.phoneNumberMappings = {"": None}   # phoneNumber: contactId
        self.numberOfContacts = 0
        self.purgedData = dict()   # contactId - parentId
        self.invertedPurgedData = dict()    # parentId - list[contactId]

    def addNewContact(self, email: str = "", phoneNumber: str = "", linkPrecedence: str = "primary", linkedId: any = None):
        """ Creates a new contact with the given details"""
        uId = self.numberOfContacts
        newContact = Contact(uId=uId, email=email,
            phoneNumber=phoneNumber, linkedId=uId, linkPrecedence=linkPrecedence,
            createdAt=getTime()
        )

        if email:
            _emailMapping = self.emailMappings.get(email, None)
            if _emailMapping:
                self.emailMappings[email].add(uId)
            else:
                self.emailMappings[email] = {uId}

        if phoneNumber:
            _phoneNumberMapping = self.phoneNumberMappings.get(phoneNumber, None)
            if _phoneNumberMapping:
                self.phoneNumberMappings[phoneNumber].add(uId)
            else:
                self.phoneNumberMappings[phoneNumber] = {uId,}

        self.users[uId] = newContact
        self.numberOfContacts += 1

        return uId

    def findContact(self, request: Request):
        """ This function will check the incoming request & perform actions(newAccount/purgeAccounts)"""
        email = request.email or ""
        phoneNumber = request.phoneNumber or ""

        emailContactIds, phContactIds = self.emailMappings.get(email, None), self.phoneNumberMappings.get(phoneNumber, None)

        if emailContactIds and phContactIds:
            cId = emailContactIds.intersection(phContactIds).copy()
            if cId:
                # The account already exists
                print("Account Already Exists")
                cId = cId.pop()
            else:
                print("Different Contacts")
                cId = self.addNewContact(email, phoneNumber, linkPrecedence="secondary")
                self.purgeData([cId])
        
        elif emailContactIds:
            # There is only email
            # Check if the contact has phoneNumber empty else create a new contact
            for _cId in emailContactIds:
                contact = self.users[_cId]
                if contact.phoneNumber == phoneNumber:
                    # The contact exists
                    cId = _cId
                    break
            else:
                # Create a new contact
                cId = self.addNewContact(email=email, phoneNumber=phoneNumber, linkPrecedence="secondary")
                # Purge the data
                self.purgeData([cId])
        
        elif phContactIds:
            # There is only phone number
            # Check if the email is empty else create a new contact

            for _pId in phContactIds:
                contact = self.users[_pId]
                if contact.email == email:
                    # The contact exists
                    cId = _pId
                    break
            else:
                cId = self.addNewContact(email=email, phoneNumber=phoneNumber, linkPrecedence="secondary")
                self.purgeData([cId])
        
        else:
            # Create a new contact
            cId = self.addNewContact(email=email, phoneNumber=phoneNumber, linkPrecedence="primary")
            self.invertedPurgedData[cId] = [cId]
            self.purgedData[cId] = cId
        
        # TODO - fetch the user data & return it
        data =  self.fetchPurgedData(cId)
        # print(data)
        return data
    
    def purgeData(self, contactIds: List[int]):
        """ This function will check for similar contacts and modify the data(primary/secondary, linkedId and other)"""
        queue = set(contactIds)
        completedContactIds = set()

        while queue:
            contactId = queue.pop()
            completedContactIds.add(contactId)
            _contact = self.users[contactId]
            _email, _phoneNumber = _contact.email, _contact.phoneNumber
            ecIds = set(self.emailMappings[_email])
            pcIds = self.phoneNumberMappings[_phoneNumber]

            if ecIds:
                newIds = ecIds.difference(completedContactIds)
                queue = queue.union(newIds)

            if pcIds:
                newIds = pcIds.difference(completedContactIds)
                queue = queue.union(newIds)

        # Fetched all the contacts that need to be modified
        rootAccId = min(completedContactIds)

        for accId in completedContactIds:
            if accId == rootAccId:
                continue
            # Update the account details to root
            contact = self.users[accId]
            contact.linkPrecedence = "secondary"
            contact.linkedId = rootAccId
            contact.updatedAt = getTime()
            self.users[accId] = contact
            self.purgedData[contact.uId] = rootAccId

        self.invertedPurgedData[rootAccId] = completedContactIds
        # print("Purged Data: ", self.purgedData)
        # print(self.invertedPurgedData)
        
    def fetchPurgedData(self, contactId: int):
        """ This function returns data of the root user along with """
        # print(contactId, self.users, self.invertedPurgedData)
        parentId = self.users[contactId].linkedId
        if parentId is None:
            # An error, no such contactId
            return {}
        
        totalContacts = self.invertedPurgedData[parentId].copy()
        print("Actual TOtla COntacts", totalContacts)
        totalContacts.remove(parentId)  # Remove the parentId
        parentEmail, parentPhoneNumber = self.users[parentId].email, self.users[parentId].phoneNumber
        totalEmails = []; totalPhoneNumbers = []

        if parentEmail:
            totalEmails.append(parentEmail)
        if parentPhoneNumber:
            totalPhoneNumbers.append(parentPhoneNumber)
        
        print(totalEmails, totalPhoneNumbers, totalContacts)

        for cId in totalContacts:
            contact = self.users[cId]
            if contact.email and contact.email not in totalEmails:
                totalEmails.append(contact.email)
            if contact.phoneNumber and contact.phoneNumber not in totalPhoneNumbers:
                totalPhoneNumbers.append(contact.phoneNumber)
        
        # print(repr(self.users))
        
        returnData = {
            "contact":{
                "primaryContactId": parentId,
                "emails": totalEmails,
                "phoneNumbers": totalPhoneNumbers,
                "secondaryContactIds": list(totalContacts) if len(totalContacts) > 0 else []
            }
        }
        return returnData

AppUsers = Users()