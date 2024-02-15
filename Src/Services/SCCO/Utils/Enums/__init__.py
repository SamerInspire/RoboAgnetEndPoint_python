from enum import Enum


class OccupationStatus(Enum):
    Status1 = 'مسودة'
    Status2 = 'بانتظار موافقة صاحب العمل'
    Status3 = 'في انتظار موافقة الموظف'
    Status4 = 'مرفوض من صاحب العمل'
    Status5 = 'مرفوض من الموظف'
    Status6 = 'موافق عليه من صاحب العمل'
    Status7 = 'في انتظار رد الداخلية'
    Status8 = 'مقبول من الداخلية'
    Status9 = 'ملغى من صاحب العمل'
    Status10 = 'ملغى من العامل'
    Status11 = 'ملغاة تلقائياَ نتيجة عدم قبول أو رفض الطلب لمدة تزيد عن 10 أيام'
    Status12 = 'مرفوض من الداخلية'
    Status13 = 'مرتبطة بطلب نقل الخدمة'
    Status14 = '.ملغاة تلقائياَ نتيجة عدم رد الداخلية لمدة تزيد عن 14 يوم'

class COAnswers(Enum):
    ChangeOccupationQIWA = 'الموظف صاحب الاقامة {{LaborerIdNo}}\n لديه طلب تغير مهنة على منصة قوى وحالته "{{StatusId}}" \n من المهنة :  "{{SourceJobId}}" الى المهنة  "{{DestinationJobId}}"\n حيث انه تم تقديم الطلب في تاريخ : {{InsertDate}}'
    NoChangeOccupation = 'الموظف صاحب الاقامة {{LaborerIdNo}} لا يوجد لديه طلب تغير مهنة على منصة قوى'
    HRSDIssueOC='الموظف صاحب الاقامة {{LaborerIdNo}} \n يوجد لديه مشكلة في طلب تغير المهنة او عكس مهنته في وزارة الموارد البشرية \n يرجى تحويل التذكرة الى خدمة المهن لتحقق من المشكلة'
    SaudiCertificate='الرجاء التحقق يمكنك اصدار شهادة سعودة للمنشأه المدخلة يرجى المحاولة مرة أخرى في حال إستمرار الإشكالية يرجى تزويدنا بصورة حديثه'
    SaudiCertificate2='المنشأه عليها الملاحظات التالية لذلك لا يمكنك اصدار شهادة السعودة'
    CertificateName='يرجى العلم بأن الاسم المسجل في شهادة السعودة هو نفسه في مكتب العمل في حال طباعة شهادة السعودة باسم اخر يرجى الضغط عل زر تحديث ثم المحاولة مرة اخرى'
    NoCertificate='لا يوجد شهادة سعودة حالتها نشطة على المشنأة المدخلة من قبلكم'
    CertificateDate='لم يتم مرور "يوم" على تاريخ انشاء شهادة السعودة لذلك لا يمكنك تحديث الشهادة الرجاء التحقق بعد يوم من تاريخ انشاء شهادة السعودة التالي {{CreationDate}}'
    CertifcatetNo='نرجو العلم انه لا يوجد للمنشاه المدخلة من قبلكم شهادة سعودة'