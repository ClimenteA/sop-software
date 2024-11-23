from common.collections import get_collection, Col


class SOPCol(Col):
    Users = "SOPUsers"
    InvitedUsers = "SOPInvitedUsers"
    Sops = "SOPSops"
    SopSearches = "SOPSearches"
    MessagesAdmin = "SOPMessagesAdmin"
    TokenBlackList = "SOPTokenBlackList"


MessagesAdminCol = get_collection(SOPCol.MessagesAdmin)
SopsCol = get_collection(SOPCol.Sops)
SopSearchesCol = get_collection(SOPCol.SopSearches)
UsersCol = get_collection(SOPCol.Users)
InvitedUsersCol = get_collection(SOPCol.InvitedUsers)
