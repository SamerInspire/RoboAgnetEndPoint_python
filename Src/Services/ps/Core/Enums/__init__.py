from enum import Enum


class PMAnswers(Enum):
    MissingPrivileges = 'المستخدم \'{{}}\' هو مدير الرقم الموحد ولديه صلاحيات ناقصة وهي \'{{}}\' '
    RedundantPrivileges = 'المستخدم \'{{}}\' لديه صلاحيات مكرره يجب حذفها وهي \'{{}}\' '
    IsNotAccountManager = 'المستخدم ليس مدير الرقم الموحد ولا يمكن إضافة الصلاحيات , الرجاء الطلب من مدير الرقم الموحد إضافة الصلاحيات المطلوبة'
    NoNeedToAddPriv = 'المستخدم بالفعل لديه كامل الصلاحيات '
    NoPreviousSubscriptions = 'يرجى العلم بانه لا يوجد إشتراكات سابقة على المنشأة \'{{}}\' '
    userNotInUserSubscription = 'يرجى العلم بأنه لا يوجد إشتراك فعال للمستخدم \'{{IdNo}}\' على المنشأة \'{{Est}}\' '

class PMQueries(Enum):
    Privileges = 'select ID from [Qiwa_MLSD_Main].[dbo].UMServiceConfiguration with(nolock) order by ID asc'
    PrivilegesInquiry = "select * from [Qiwa_MLSD_Main].[dbo].userprivileges u  with(nolock)   inner Join UMServiceConfiguration L on U.Privilege_ID = L.ID where ID_NO = '{{idNo}}'  and Establishment_Sequence = '{{estSeq}}' and Labor_Office_ID ='{{estLab}}' and Subscription_Status_ID = 1 order by u.ID asc"
    RedundantPrivilegs = "select Privilege_ID , count(*) from UserPrivileges where ID_NO = '{{idNo}}' and Establishment_Sequence = '{{estSeq}}' and Labor_Office_ID = '{{estLab}}' and Subscription_Status_ID = 1 group by Privilege_ID order by Privilege_ID  asc "
    AccountManagerInUserSubscription = "select * from Qiwa_MLSD_Main.dbo.UserSubscriptions With (NoLOCK) where SequenceNumber = '{{estSeq}}' and EstablishmentLaborOfficeId = '{{estLab}}' "
    EstablishmentsAccountManager = 'select * from MOL_GEneration_PHASEI.dbo.MOL_VwUserEstablishmentsAccountManager With (NoLOCK) where EstablishmentSequenceNumber = \'{{par2}}\' and EstablishmentLaborOfficeId = \'{{par1}}\' and UserType = 1 '
    userInAccountManager = "select UserType , IDNO from MOL_GEneration_PHASEI.dbo.MOL_VwUserEstablishmentsAccountManager With (NoLOCK) where EstablishmentSequenceNumber = \'{{par2}}\' and EstablishmentLaborOfficeId = \'{{par1}}\' and UserType in ('1' , '2')"
    userInUserSubscription = "select (select idno from Qiwa_MLSD_Main.dbo.users with (nolock) where id =  UserSubscriptions.user_id) as ID from Qiwa_MLSD_Main.dbo.UserSubscriptions with (nolock) where SequenceNumber = '{{estSeq}}' and LaborOfficeId = '{{estLab}}' and StatusId = 1 and User_Id in (select id from Qiwa_MLSD_Main.dbo.users with (nolock) where IDNO =  '{{idNo}}')"
    isUserOnTheJob = "select * from MOL_GENERATION_PHASEI.dbo.MOL_laborer with(nolock) where FK_CurrentLaborOfficeId  = '{{estLab}}' and SequenceNumber = '{{estSeq}}' and IdNo = '{{idNo}}' and FK_LaborerStatusId = 1"



#T =Test = select distinct User_Id,LaborOfficeId,SequenceNumber,RequesterIdNo,AmountPerUser,UnifiedNumber from UserSubscriptions where PaymentReference ='QW-UM-HP-23-4DDA389B18-000000003292955'

# Transfer Subscription Queries

    UserEmail = 'select Email from users where IDNO = \'{{IdNo}}\''
    UnifiedNumberSubscriptions ='select LaborOfficeId , SequenceNumber ,  from dbo.UserSubscriptions where UnifiedNumber= \'{{UnifiedNum}}\' and PaymentReference = \'{{PayRef}}\' SequenceNumberorder by Creationdate desc '
    VisitVisaRequest = 'select * from EstablishingVisaTier where EstablishmentSequence = \'{{estSeq}}\' and LaborOfficeId = \'{{estLab}}\''
    ExpansionVisaRequest = 'select * from VisitVisaRequest where EstablishmentSequence = \'{{estSeq}}\' and LaborOfficeId = \'{{estLab}}\''
    IssuedVisas = 'select * from IssuedVisas where VisaLaborOfficeId = \'{{estLab}}\' and VisaSequenceNumber = \'{{estSeq}}\' and visastatusid = 1 '
    ChangeSponsorRequestDetails = 'select * from ChangeSponsorRequestDetails where DestinationLaborOfficeId = \'{{estLab}}\' and DestinationEstablishmentSequence = \'{{estSeq}}\' and StatusId = 5'

