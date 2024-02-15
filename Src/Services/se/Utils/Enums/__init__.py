from enum import Enum


class ETStatus(Enum):
    Status1 = 'مسوّدة'
    Status2 = 'بانتظار موافقة صاحب العمل الحالي'
    Status3 = 'بانتظار موافقة الموظف'
    Status4 = 'بانتظار استكمال عملية النقل فى وزارة الداخلية بواسطة صاحب العمل الجديد'
    Status5 = 'مقبول'
    Status6 = 'مرفوض من الداخلية'
    Status7 = 'بانتظار إكمال فترة الإشعار'
    Status8 = 'ملغاة تلقائياَ نتيجة عدم قبول أو رفض الطلب لمدة تزيد عن 14 يوم'
    Status9 = 'مرفوض من الموظف'
    Status10 = 'مرفوض من صاحب العمل الحالي'
    Status11 = 'ملغاة من صاحب العمل الجديد'
    Status12 = 'منتهي بسبب عدم استكمال الطلب من صاحب العمل الجديد'
    Status13 = 'قيد المعالجة'
    Status14 = 'ملغي لعدم إستلام الطلب من الداخلية'
    Status15 = 'ملغي من الموظف'

class ETAnswers(Enum):
    HasChangeSponsor = 'الموظف صاحب الاقامة "{{LaborerIdNo}}" لديه طلب نقل على منصة قوى وحالته "{{ETStatus}}"\n من المنشاه رقم {{SourceEstablishmentNumber}} الى المنشاه رقم {{DestinationEstablishmentNumber}}'
    NoChangeSponsor  = 'الموظف صاحب الاقامة {{LaborerIdNo}} لا يوجد لديه طلب نقل على منصة قوى'
    Cantransfer='نرجوالعلم يمكنك نقل الموظف صاحب الاقامة  "{{LaborerIdNo}}" الى المنشاه المختارة الرجاء التحقق'
    EntityNotValid='الرجاء التحقق من رقم الكيان في انظمة وزارة الموارد البشرية حيث انه غير ظاهر'
    ChangeSponsorRelease = 'الموظف صاحب الاقامة "{{LaborerIdNo}}" لديه طلب نقل على منصة قوى وحالته "{{ETStatus}}" من المنشاه رقم {{SourceEstablishmentNumber}} الى المنشاه رقم {{DestinationEstablishmentNumber}} \n\n ملاحظة :\n يمكن تقليل فترة الاشعار من خلال صاحب العمل الحالي حيث انها تنتهي في تاريخ {{Realase}}'
