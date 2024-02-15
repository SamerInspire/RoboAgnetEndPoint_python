from enum import Enum


class StatusPayment(Enum):
    Status2 = 'معلقة'
    Status3 = 'مدفوعة'
    Status4 = 'مرفوضة'
    Status5 = 'تم ارجاع المبلغ'


class UMAnswers(Enum):
    NotSupportedEst = ' \n \n \n \n يرجى الإفادة بأن النشاط الخاص بالمنشأة "{{MainEconomicActivity}}" غير مخدوم في قوى'
    MoreThanOneAccount =  ' \n \n \n \n المنشأة رقم {{estNumber}} يوجد عليها عدد "{{NoAccounts}}" مدراء رقم موحد يرجى دعمكم'
    ZeroAccounts = ' \n \n \n \n لا يوجد مدير رقم موحد للمنشأة في وزارة الموارد البشرية والتنمية الاجتماعية.\nالرجاء تسجيل مدير الرقم الموحد في أنظمة وزارة الموارد البشرية'
    NotTheAccountManager = '\n \n \n \nنفيدكم بأنه بحسب بيانات مكتب العمل فإن مدير الرقم الموحد للمنشأة "{{estNumber}}" هو صاحب الهوية اللتي تنتهي ب ({{last3Digits}})\nيرجى الطلب منه بإنشاء إشترك لكم , في حال وجود مالك جديد للمنشأة يرجى تعيين المالك الجديد ك مدير للرقم الموحد في أنظمة وزارة الموارد البشرية'
    AccountNotActive = '\n \n \n \n حساب مدير الرقم الموحد غير نشط في أنظمة وزارة الموارد البشرية والتنمية الاجتماعية.'
    AccountNotRegistered = '\n \n \n \n مدير الرقم الموحد غير مسجل في الخدمات الإلكترونية لوزارة الموارد البشرية والتنمية الاجتماعية.'
    WorkspaceDown = ' \n GetQiwaWorkspaceEstablishments API is Down , \n \n Please Try Again Later \n \n \n \n'
    PaymentRefCancel = ' \n \n \n \n الرجاء رفع تذكرة الى فريق P2H \n لوجود عملية دفع لم يتم ربطها في الاشتراك،الرجاء التحقق'
    NoPaymentRef = '\n \n \n \n صاحب الهوية {{IdNumber}} لا يوجد لديه عمليات دفع حالتها مرفوضة او تم ارجاع المبلغ على منصة قوى'
    EmployeePayment = ' صاحب الهوية {{IdNumber}} يوجد لديه العمليات الدفع التالية على منصة قوى:\n \nالرجاء رفع تذكرة الى P2H لوجود عملية دفع غير مرتبطة بلأشتراك\n'
    EmployeePayment2 = '\n \n \n \n  صاحب الهوية {{IdNumber}} لا يوجد لديه عمليات دفع حالتها تم ارجاع المبلغ و معلقة و مرفوضة خلال مدة سنة فقط\n'
    ListPayment = ' \n \n \n \n عملية الدفع رقم  \n "{{PaymentReference}}" \n في تاريخ "{{InsertDate}}" وحالتها "{{StatusId}}"\n'
    PaymentAnswer2 = ' \n \n \n \n الرجاء المحاولة مرة اخرى بعد ساعة \n'
    PaymentAnswer4 = 'الرجاء ارسال العمليات التالية الى استاذ سعود لتحقق من HyperPay \n في حال كانت مرفوضة في HYPERPAY الرجاء الرد على العميل بالتالي \nفي حال تم خصم منكم مبالغ الرجاء مراجعة البنك والرجاء المحاولة مرة اخرى لتجديد الاشتراك \n'
    PaymentAnswer5 = 'الرجاء التحقق مع تيم P2H \n في حال لم تكن مرفوضة الرجاء الطلب منهم تحويلها الى مرفوضة وبعد تحويلها الى مرفوضة الرجاء اغلاق التذكرة مع العميل \n'


class UMQueries(Enum):
    EstablishmentsAccountManager = 'select * from MOL_GEneration_PHASEI.dbo.MOL_VwUserEstablishmentsAccountManager With (NoLOCK) where EstablishmentSequenceNumber = \'{{par2}}\' and EstablishmentLaborOfficeId = \'{{par1}}\' and UserType = 1 '
    MolUserInfo = 'select * from MOL_GEneration_PHASEI.dbo.mol_user with(nolock) where ID_NUMBER = \'{{idNo}}\' '
    NotProvidedActivity = 'select * from MoL_Nitaqat_III.dbo.Economic_Activity_Mapping_Details with (nolock) where Sub_Economic_Activity_Id = {{Sub_Economic_Activity_Id}} and Main_Economic_Activity_Id = {{Main_Economic_Activity_Id}} and isHidden = 1 '
    EstablishmentHistory = 'select Calculation_Type_Id ,Economic_Activity_Id, Entity_Color,Entity_Color_Id, Run_Date,Is_Below_Green,Entity_Saudi_Percentage,Sub_Economic_Activity_Id,Main_Economic_Activity_Id From MOL_NITAQAT_III.dbo.ESTABLISHMENT_EVALUATION_history with (nolock)  where sequence_number={{par2}} AND Labor_Office_Id={{par1}} ORDER BY Run_Date  desc'
    PaymentUserSub = 'select PaymentReference,InsertDate,StatusId from QIWA_Payment.dbo.Payment  with(nolock)  where p.IDNO =\'{{LaborerIdNo}}\' and statusId=2 and p.ProductId= 4'
    PaymentRefundedReject = 'select PaymentReference,StatusId,InsertDate from QIWA_Payment.dbo.Payment with(nolock) where StatusId in () and p.IDNO =\'{{LaborerIdNo}}\''
    PaymentSelect = 'select p.PaymentReference, InsertDate, p.StatusId from QIWA_Payment.dbo.Payment P with(nolock) left outer join dbo.usersubscriptions u with(nolock) on p.PaymentReference = u.PaymentReference where p.IDNO =\'{{IdNumber}}\' and p.statusId=3 and p.ProductId= 4 and u.PaymentReference is null'
    AllPayment = 'select PaymentReference,InsertDate,StatusId from  QIWA_Payment.dbo.Payment with(nolock) where IDNO =\'{{IdNumber}}\' and InsertDate >= DATEADD(year, -1, GETDATE())'

    NotSupportedActivity = 'select * from MoL_Nitaqat_III.dbo.Economic_Activity_Mapping_Details with (nolock) where Sub_Economic_Activity_Id = {{Sub_Economic_Activity_Id}} and Main_Economic_Activity_Id = {{Main_Economic_Activity_Id}} and isHidden = 1 '
    insertInvoice = "INSERT INTO dbo.Unified_Invoices (TemplateKey  , TemplateName  , TemplateContent  , TemplateContentName  , MessageSubject  , MessageFromEmail  , MessageFromName  , MessageToEmail  , [merge]  , merge_language , MessageDetails , CreationDate  , TotalExcludingVat  , TotalTaxable , TotalVat  , Total , InvoiceTypeId , UnifiedNumber  , InvoiceId  , IsHandled  , LaborOfficeId  , SequenceNumber , SupplyDate ) values ( '0vMrTJDN9ChIe8iBYxknmg', 'Unified Invoice Template AR', 'Qiwa Invoice', 'Qiwa Invoice', N'فاتورة إشتراك', 'noreply@qiwa.sa', N'قوى', {{userEmailVal}} , 'True', 'handlebars', N'{ \"global_merge_vars\": [ { \"name\": \"invoice_id\", \"content\": \"{{PaymentRefVal}}\" }, { \"name\": \"invoice_issue_date\", \"content\": \"{{InvoiceIssueDateVal}}\" }, { \"name\": \"date_of_supply\", \"content\": \"{{DateOfSupplyVal}}\" }, { \"name\": \"company_name_to\", \"content\": \"{{CompanyNameVal}}\" }, { \"name\": \"building_number_to\", \"content\": \"{{BuildingNumberToVal}}\" }, { \"name\": \"district_to\, \"content\": \"{{DistrictNoToVal}}\" }, { \"name\": \"street_name_to\", \"content\": \" {{StreetNameToVal}}\" }, { \"name\": \"city_to\", \"content\": \"{{CityToVal}}\" }, { \"name\": \"additional_number_to\", \"content\": \"{{AdditionalNoToVal}}\" }, { \"name\": \"vat_number_to\", \"content\": \"{{VatNoVal}}\" }, { \"name\": \"country_to\", \"content\": \"المملكة العربية السعودية\" }, { \"name\": \"details\", \"content\": [ { \"unit_price\": \"{{UnitePriceVal}}\", \"user_name\": \"{{UserNameVal}}\", \"IdNo\": \"{{IdNoVal}}\", \"quantity\": 1, \"tax_amount\": {{TaxAmountVal}}, \"taxable_amount\": {{TaxableAmountVal}}, \"tax_rate\": \"15%\", \"item_subtotal\": {{ItemSubtotalVal}}, \"service_details\": \"اضافة اشتراكات المستخدمين على منصة قوى\" } ] }, { \"name\": \"total_excluding_vat\", \"content\": {{TotalExecludingVatVal}} }, { \"name\": \"total_taxable\", \"content\": {{TotalExecludingVatVal}} }, { \"name\": \"total_vat\", \"content\": {{TaxAmountVal}} }, { \"name\": \"total\", \"content\": {{ItemSubtotalVal}} } ] }', '{{DateOfSupplyVal}}', '{{TaxableAmountVal}}', '{{TaxableAmountVal}}', '{{TaxAmountVal}}', '{{ItemSubtotalVal}}', '3', '{{UnifiedNumberVal}}', '{{PaymentRefVal}}', '0', '{{estLab}}', '{{estSeq}}', '{{DateOfSupplyVal}}' )"

    GetAllSubscriptionReferences = 'select PaymentReference  , StartDate from Qiwa_MLSD_Main.dbo.UserSubscriptions with (nolock) where SequenceNumber =\'{{estSeq}}\' and LaborOfficeId= \'{{estLab}}\' order by StartDate desc'
    GetUnifiedNumber='select UnifiedNumber from Qiwa_MLSD_Main.dbo.UserSubscriptions with (nolock) where SequenceNumber =\'{{estSeq}}\' and LaborOfficeId= \'{{estLab}}\' order by StartDate desc'
    GetInvoiceAmount = 'select Amount from Qiwa_Payment.dbo.Payment  with (nolock) where PaymentReference={{PaymentReference}} order by InsertDate desc'
    GetInvoiceIds = 'select InvoiceId from Unified_Invoices where InvoiceId in ({{invoiceId}}) and InvoiceTypeId = 3'
    UserInvoiceInfo = 'select IDNO ,Name , Email  from users where id = {{IdNo}}'
    EstablishmentAddress = 'Select  BuildingNumber ,District , Street ,City , AdditionalNo  from EstablishmentAddress where EstablishmentSequenceID = {{par2}} and LaborOfficeID = {{par1}}'
    EstablishmentVat = 'select VATAccountNumber , CompanyName from EstablishmentVAT where EstablishmentSequenceID = {{par2}} and LaborOfficeID = {{par1}}'
    #GetAllSubscriptionReferences = 'select PaymentReference ,  from Qiwa_MLSD_Main.dbo.UserSubscriptions with (nolock) where SequenceNumber =\'{{estSeq}}\' and LaborOfficeId= \'{{estLab}}\' order by StartDate desc'
    GetPaymentReferenceAmount = 'select * from Qiwa_Payment.dbo.Payment  with (nolock) where PaymentReference={{PaymentRef}} order by InsertDate desc'

