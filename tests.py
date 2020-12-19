import pytest
from course import sort_students, Student, Course
from survey import Question, MultipleChoiceQuestion, NumericQuestion, \
    YesNoQuestion, CheckboxQuestion, Answer, Survey
from criterion import InvalidAnswerError, HomogeneousCriterion, \
    HeterogeneousCriterion, LonelyMemberCriterion, Criterion
from grouper import slice_list, windows, Grouper, AlphaGrouper, RandomGrouper, \
    GreedyGrouper, WindowGrouper, Group, Grouping


class TestStudent:
    def test_string_student(self) -> None:
        s = Student(1, 'Maria')
        assert str(s) == 'Maria'  # return str

    def test_has_answer_student(self) -> None:
        s = Student(1, 'Maria')
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        assert not s.has_answer(numeric)  # did not answer

        # not valid answer
        a0 = Answer(True)
        s.set_answer(numeric, a0)
        assert not s.has_answer(numeric)

        a1 = Answer(2)
        s.set_answer(numeric, a1)
        assert s.has_answer(numeric)

    def test_set_answer_student(self) -> None:
        s = Student(1, 'Maria')
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        a1 = Answer(2)
        assert s.set_answer(numeric, a1) is None  # return None
        a2 = Answer(True)
        assert s.set_answer(numeric, a2) is None  # works for invalid
        assert s._answers == {2: a2}

    def test_get_answer_student(self) -> None:
        s = Student(1, 'Maria')
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        invalid = NumericQuestion(5, '2+2=', 3, 5)  # its answer to be invalid
        none = YesNoQuestion(6, 'Do you like omelet?')  # not answered

        # answers
        a1 = Answer('A')
        a2 = Answer(2)

        # record the answer to question
        s.set_answer(numeric, a2)
        s.set_answer(invalid, a1)  # invalid

        # has an answer and is valid
        assert s.has_answer(numeric)
        assert not s.has_answer(invalid)  # invalid
        assert not s.has_answer(none)  # did not answer

        # get the answer (no matter right or wrong)
        assert s.get_answer(numeric) == a2  # return Answer
        assert s.get_answer(invalid) == a1
        assert s.get_answer(none) is None  # return None if DNE

    def test_student_class(self) -> None:
        # student
        sabrina = Student(1, 'sabrina')
        assert sabrina.id == 1
        assert sabrina.name == str(sabrina)
        assert sabrina._answers == {}

        # question
        multi = MultipleChoiceQuestion(11, 'A or B', ['A', 'B'])
        num = NumericQuestion(22, '1-3', 1, 3)
        yesno = YesNoQuestion(33, 'True or False')
        check = CheckboxQuestion(44, 'A or B', ['A', 'B'])

        # answers
        a = Answer('A')
        b = Answer('B')
        one = Answer(1)

        # f: str -> str
        assert str(sabrina) == 'sabrina'

        # f: set_answer(Question, Answer) -> None
        assert sabrina.set_answer(multi, b) is None
        sabrina.set_answer(multi, a)
        sabrina.set_answer(num, one)
        sabrina.set_answer(yesno, a)  # invalid
        # <check> not answered

        # f: has_answer(Question) -> bool
        assert sabrina.has_answer(multi)
        assert sabrina.has_answer(num)
        assert not sabrina.has_answer(yesno)  # invalid thus False
        assert not sabrina.has_answer(check)  # unanswered thus False
        assert sabrina._answers == {11: a, 22: one, 33: a}

        # f: get_answer(Question) -> Optional(Answer)
        assert sabrina.get_answer(multi) == a
        assert sabrina.get_answer(num) == one
        assert sabrina.get_answer(yesno) == a  # invalid but works
        assert sabrina.get_answer(check) is None  # DNE


class TestCourse:
    def test_enroll_students_course(self) -> None:
        s1 = Student(0, 'Leo')
        s2 = Student(1, 'Leo')
        s3 = Student(2, 'Mike')
        s4 = Student(0, 'Mark')  # the duplicate
        s5 = Student(3, '')  # the empty

        yes = [s1, s2, s3]
        dup = [s1, s2, s4]  # with dup
        emp = [s1, s2, s5]  # with emp

        c = Course('Baking')
        assert c.enroll_students(dup) is None  # return None
        assert len(c.students) == 0
        assert c.enroll_students(emp) is None
        assert len(c.students) == 0
        assert c.enroll_students(yes) is None
        assert c.students[0] == s1

    def test_all_answered_course(self) -> None:
        s1 = Student(0, 'Leo')
        s2 = Student(1, 'Leo')
        ss = [s1, s2]

        c = Course('Fishing')
        c.enroll_students(ss)

        q = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        qs = [q]
        s = Survey(qs)

        assert not c.all_answered(s)  # no answer
        s1.set_answer(q, Answer(2))
        assert not c.all_answered(s)  # lack of answer
        s2.set_answer(q, Answer(4))
        assert not c.all_answered(s)  # invalid answer
        s2.set_answer(q, Answer(2))
        assert c.all_answered(s)

    def test_get_students_course(self) -> None:
        s1 = Student(0, 'Leo')
        s2 = Student(1, 'Leo')
        s3 = Student(2, 'Mike')
        s4 = Student(0, 'Mark')  # the duplicate
        s5 = Student(3, '')  # the empty

        yes = [s3, s2, s1]
        dup = [s1, s2, s4]
        emp = [s1, s2, s5]

        c = Course('Baking')
        c.enroll_students(dup)
        assert len(c.get_students()) == 0  # not enrolled
        c.enroll_students(emp)
        assert len(c.get_students()) == 0  # not enrolled
        c.enroll_students(yes)
        assert c.get_students() == (s1, s2, s3)  # in id order

    def test_course_class(self) -> None:
        baking = Course('Baking')
        assert baking.name == 'Baking'
        assert baking.students == []

        # students
        sabrina = Student(1, 'sabrina')
        luke = Student(2, 'luke')
        harvey = Student(3, 'harvey')
        clone_harvey = Student(3, 'harvey')
        ben = Student(4, 'ben')
        no_name = Student(5, '')

        # lists of students
        girl = [sabrina]
        boy = [harvey]
        clone = [clone_harvey, ben]
        none = [no_name, ben]

        # f: enroll_students(List[Student]) -> None
        assert baking.enroll_students(girl) is None
        assert baking.enroll_students(boy) is None
        assert baking.enroll_students(clone) is None
        assert baking.enroll_students(none) is None
        assert len(baking.students) == 2
        assert baking.students[0] == sabrina
        assert baking.students[1] == harvey

        # f: all_answered(Survey) -> bool
        num = NumericQuestion(22, '1-3', 1, 3)
        one = Answer(1)
        zero = Answer(0)
        # assert num.validate_answer(one)
        # assert not num.validate_answer(zero)

        survey = Survey([num])
        assert not baking.all_answered(survey)

        sabrina.set_answer(num, one)
        # assert sabrina._answers == {22: one}
        assert not baking.all_answered(survey)  # only one answer

        harvey.set_answer(num, zero)
        # assert harvey._answers == {22: zero}
        assert not baking.all_answered(survey)  # only one valid answer

        harvey.set_answer(num, one)
        # assert harvey._answers == sabrina._answers
        # assert sabrina.has_answer(num) and harvey.has_answer(num)
        # assert survey.get_questions() == [num]
        assert baking.all_answered(survey)  # all answer, all valid

        # f: get_students() -> Tuple[Student]
        baking.enroll_students([luke])
        assert baking.students[2] == luke
        assert baking.get_students() == (sabrina, luke, harvey)


class TestMultipleChoiceQuestion:
    def test_isinstance(self) -> None:
        mcq = MultipleChoiceQuestion(0, 'text', ['A', 'B'])
        assert isinstance(mcq, Question)
        assert isinstance(mcq, MultipleChoiceQuestion)

    def test_string_mcq(self) -> None:
        mcq = MultipleChoiceQuestion(0, 'Which one is ice cream?',
                                     ['A. ice cream', 'B. apple juice'])
        assert str(mcq) == ('Which one is ice cream?\n'
                            'A. ice cream\nB. apple juice')

    def test_validate_answer_mcq(self) -> None:
        mcq = MultipleChoiceQuestion(0, 'Which one is ice cream?',
                                     ['A. ice cream', 'B. apple juice'])
        options = ['A. ice cream', 'B. apple juice']
        for option in options:
            assert mcq.validate_answer(Answer(option))
        assert not mcq.validate_answer(Answer('ice cap'))  # invalid answer
        assert not mcq.validate_answer(Answer(3))  # invalid answer

    def get_similarity_mcq(self) -> None:
        mcq = MultipleChoiceQuestion(0, 'Which one is ice cream?',
                                     ['A. ice cream', 'B. apple juice'])
        a1 = Answer('A. ice cream')
        a2 = Answer('B. apple juice')
        assert mcq.get_similarity(a1, a1) == 1.0  # equal content
        assert mcq.get_similarity(a1, a2) == 0.0  # not equal

    def test_multiplechoice_question_class(self) -> None:
        # question
        multiple = MultipleChoiceQuestion(11, 'A or B', ['A', 'B'])
        assert multiple.id == 11
        assert multiple.text == 'A or B'
        assert multiple._options == ['A', 'B']

        # answers
        aa = Answer('A')
        aaa = Answer('A')
        bb = Answer('B')
        cc = Answer('C')

        # f: str -> str
        assert str(multiple) == 'A or B\nA\nB'

        # f: validate_answer(Answer) -> bool
        assert multiple.validate_answer(aa)
        assert multiple.validate_answer(bb)
        assert not multiple.validate_answer(cc)  # not in list

        # f: get_similarity(Answer, Answer) -> float
        # equal -> 1.0. not -> 0.0
        assert isinstance(multiple.get_similarity(aa, aa), float)
        assert multiple.get_similarity(aa, aaa) == 1.0
        assert multiple.get_similarity(aa, bb) == 0.0


class TestNumericQuestion:
    def test_isinstance(self) -> None:
        nq = NumericQuestion(0, 'text', 0, 1)
        assert isinstance(nq, Question)
        assert isinstance(nq, NumericQuestion)

    def test_string_nq(self) -> None:
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        assert str(numeric) == 'Pick a number from 1-3 (inclusive)\n' \
                               '(The answer is an integer between 1 and 3)'

    def test_validate_answer_nq(self) -> None:
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        assert not numeric.validate_answer(Answer(True))  # not int
        assert not numeric.validate_answer(Answer(2.0))  # not int
        assert numeric.validate_answer(Answer(1))  # equal to min
        assert numeric.validate_answer(Answer(3))  # equal to max
        assert numeric.validate_answer(Answer(2))  # in the middle

    def test_get_similarity_nq(self) -> None:
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        a1 = Answer(1)
        a2 = Answer(3)
        assert numeric.get_similarity(a1, a1) == 1.0  # equal -> 1.0
        assert numeric.get_similarity(a1, a2) == 0.0  # a1 min, a2 max -> 0.0

    def test_numeric_question_class(self) -> None:
        # question
        numeric = NumericQuestion(22, '1-3', 1, 3)
        assert numeric.id == 22
        assert numeric.text == '1-3'
        assert numeric._min == 1
        assert numeric._max == 3

        # answers
        zero = Answer(0)
        one = Answer(1)
        two = Answer(2)
        three = Answer(3)
        four = Answer(4)

        # f: str -> str
        assert str(numeric) == '1-3\n(The answer is an integer between 1 and 3)'

        # f: validate_answer(Answer) -> bool
        assert not numeric.validate_answer(zero)
        assert numeric.validate_answer(one)  # min
        assert numeric.validate_answer(two)
        assert numeric.validate_answer(three)  # max
        assert not numeric.validate_answer(four)

        # f: get_similarity(Answer, Answer) -> float
        # same -> 1.0, min and max -> 0.0,
        # else: 1.0 - abs(a1 - a2) / (max - min)
        assert numeric.get_similarity(one, one) == 1.0
        assert numeric.get_similarity(one, three) == 0.0
        assert numeric.get_similarity(three, one) == 0.0
        assert numeric.get_similarity(one, two) == 0.5
        assert numeric.get_similarity(two, three) == 0.5


class TestYesNoQuestion:
    def test_isinstance(self) -> None:
        ynq = YesNoQuestion(0, 'text')
        assert isinstance(ynq, Question)
        assert isinstance(ynq, YesNoQuestion)

    def test_string_ynq(self) -> None:
        yesno = YesNoQuestion(3, 'Are people crazy?')
        assert str(yesno) == 'Are people crazy? (True / False)'

    def test_validate_answer_ynq(self) -> None:
        yesno = YesNoQuestion(3, 'Are people crazy?')
        assert yesno.validate_answer(Answer(True))  # bool
        assert yesno.validate_answer(Answer(False))  # bool
        assert not yesno.validate_answer(Answer(1))  # not bool
        assert not yesno.validate_answer(Answer(1.0))  # not bool
        assert not yesno.validate_answer(Answer('True'))  # not bool

    def test_get_similarity_ynq(self) -> None:
        yesno = YesNoQuestion(3, 'Are people crazy?')
        a1 = Answer(True)
        a2 = Answer(False)
        assert yesno.get_similarity(a1, a1) == 1.0  # equal
        assert yesno.get_similarity(a1, a2) == 0.0  # not equal

    def test_yesno_question_class(self) -> None:
        # question
        yesno = YesNoQuestion(33, 'T or F')
        assert yesno.id == 33
        assert yesno.text == 'T or F'

        # answers
        t = Answer(True)
        tt = Answer(True)
        f = Answer(False)
        # f: str -> str
        assert str(yesno) == 'T or F (True / False)'

        # f: validate_answer(Answer) -> bool
        assert yesno.validate_answer(t)
        assert yesno.validate_answer(f)
        assert not yesno.validate_answer(Answer('False'))  # str
        assert not yesno.validate_answer(Answer(1))  # int
        assert not yesno.validate_answer(Answer(1.0))  # float
        assert not yesno.validate_answer(
            Answer(['False', 'True']))  # list of str
        assert not yesno.validate_answer(Answer([False, True]))  # list of bool

        # f: get_similarity(Answer, Answer) -> float
        # equal -> 1.0. not -> 0.0
        assert yesno.get_similarity(t, tt) == 1.0
        assert yesno.get_similarity(t, f) == 0.0


class TestCheckboxQuestion:
    def test_isinstance(self) -> None:
        cbq = CheckboxQuestion(0, 'text', ['A', 'B'])
        assert isinstance(cbq, Question)
        assert isinstance(cbq, CheckboxQuestion)

    def test_string_cbq(self) -> None:
        check = CheckboxQuestion(4, 'Which of them can be red?',
                                 ['A. apple', 'B. cherry', 'C. banana'])
        assert str(check) == 'Which of them can be red?\n' \
                             'A. apple\nB. cherry\nC. banana'

    def test_validate_answer_cbq(self) -> None:
        check = CheckboxQuestion(4, 'Which of them can be red?',
                                 ['A. apple', 'B. cherry', 'C. banana'])
        emp = Answer([])  # empty list
        dup = Answer(['A. apple', 'B. cherry', 'A. apple'])
        single = Answer(['A. apple'])  # 1 possible answer
        al = Answer(['A. apple', 'B. cherry', 'C. banana'])
        more = Answer(['A. apple', 'B. cherry', 'C. banana', 'D. beef'])
        string = Answer('A. apple')
        assert not check.validate_answer(emp)
        assert not check.validate_answer(dup)
        assert not check.validate_answer(more)
        assert not check.validate_answer(string)  # strings do not work
        assert check.validate_answer(single)
        assert check.validate_answer(al)

    def test_get_similarity_cbq(self) -> None:
        check = CheckboxQuestion(4, 'Which of them can be red?',
                                 ['A. apple', 'B. cherry', 'C. banana'])
        a1 = Answer(['A. apple', 'B. cherry'])
        a2 = Answer(['B. cherry', 'C. banana'])
        assert check.get_similarity(a1, a1) == 1.0
        assert check.get_similarity(a1, a2) == 0.3333333333333333

    def test_checkbox_question_class(self) -> None:
        # question
        check = CheckboxQuestion(11, 'A or B', ['A', 'B'])
        assert check.id == 11
        assert check.text == 'A or B'
        assert check._options == ['A', 'B']

        # answers
        a = Answer(['A'])
        b = Answer(['B'])
        ab = Answer(['A', 'B'])
        bb = Answer(['B', 'B'])
        cc = Answer(['C'])

        # f: str -> str
        assert str(check) == 'A or B\nA\nB'

        # f: validate_answer(Answer) -> bool
        assert check.validate_answer(a)
        assert check.validate_answer(b)
        assert check.validate_answer(ab)
        assert not check.validate_answer(Answer([]))  # empty
        assert not check.validate_answer(bb)  # not unique
        assert not check.validate_answer(cc)  # not in list

        # f: get_similarity(Answer, Answer) -> float
        # common / unique
        assert check.get_similarity(a, a) == 1.0
        assert check.get_similarity(a, b) == 0.0
        assert check.get_similarity(a, ab) == 0.5
        assert check.get_similarity(ab, ab) == 1.0


class TestAnswer:
    def test_is_valid_answer(self) -> None:
        multiple = MultipleChoiceQuestion(1, 'Which is peach?',
                                          ['A. peach', 'B. banana'])
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        yesno = YesNoQuestion(3, 'Are people crazy?')
        check = CheckboxQuestion(4, 'Which of them can be red?',
                                 ['A. apple', 'B. cherry', 'C. banana'])

        string = Answer('A. peach')
        num = Answer(2)
        bol = Answer(True)
        lst = Answer(['A. apple', 'B. cherry'])
        assert string.is_valid(multiple)
        assert not string.is_valid(numeric)
        assert not string.is_valid(yesno)
        assert not string.is_valid(check)

        assert num.is_valid(numeric)
        assert not num.is_valid(yesno)
        assert not num.is_valid(check)
        assert not num.is_valid(multiple)

        assert bol.is_valid(yesno)
        assert not bol.is_valid(multiple)
        assert not bol.is_valid(check)
        assert not bol.is_valid(numeric)

        assert lst.is_valid(check)
        assert not lst.is_valid(numeric)
        assert not lst.is_valid(multiple)
        assert not lst.is_valid(yesno)

    def test_answer_class(self) -> None:
        multiple = MultipleChoiceQuestion(11, 'A or B', ['A', 'B'])
        a = Answer('A')
        b = Answer('B')
        c = Answer('C')
        assert a.content == 'A'
        assert b.content == 'B'
        assert a.is_valid(multiple)
        assert b.is_valid(multiple)
        assert not c.is_valid(multiple)


class TestCriterion:
    def test_invalid_answer(self) -> None:
        # criterion
        homo = HomogeneousCriterion()
        hetero = HeterogeneousCriterion()
        lonely = LonelyMemberCriterion()

        # question and invalid answer
        yesno = YesNoQuestion(33, 'T or F')
        one = Answer(1)

        with pytest.raises(InvalidAnswerError):
            homo.score_answers(yesno, [one])
        with pytest.raises(InvalidAnswerError):
            hetero.score_answers(yesno, [one])
        with pytest.raises(InvalidAnswerError):
            lonely.score_answers(yesno, [one])


class TestHomogeneousCriterion:
    def test_isinstance(self) -> None:
        c = HomogeneousCriterion()
        assert isinstance(c, Criterion)
        assert isinstance(c, type(HomogeneousCriterion()))

    def test_score_answers_homo(self) -> None:
        numeric = NumericQuestion(2, 'A number bt. 1 and 3 (inclusive)', 1, 3)

        _min = Answer(1)
        _max = Answer(3)
        no = Answer(0)

        single_invalid = [no]
        invalid = [_max, no]
        single = [_min]
        valid = [_min, _max]
        complex_valid = valid + [Answer(2)]

        try:  # single but invalid
            HomogeneousCriterion.score_answers(
                HomogeneousCriterion, numeric, single_invalid)
        except InvalidAnswerError:
            pass
        try:  # multiple contain invalid
            HomogeneousCriterion.score_answers(
                HomogeneousCriterion, numeric, invalid)
        except InvalidAnswerError:
            pass

        # single and valid
        assert HomogeneousCriterion.score_answers(
            HomogeneousCriterion, numeric, single) == 1.0

        # multiple and valid
        assert HomogeneousCriterion.score_answers(
            HomogeneousCriterion, numeric, valid) == 0.0
        assert HomogeneousCriterion.score_answers(
            HomogeneousCriterion, numeric, complex_valid) == 0.3333333333333333

    def test_homogeneous_criterion_class(self) -> None:
        # question
        multiple = MultipleChoiceQuestion(11, 'A or B', ['A', 'B'])
        numeric = NumericQuestion(22, '1-3', 1, 3)

        # answer
        aa = Answer('A')
        bb = Answer('B')
        one = Answer(1)
        two = Answer(2)
        three = Answer(3)

        # answers
        single_m = [aa]
        single_n = [one]

        double_same_m = [aa, aa]
        double_diff_m = [aa, bb]
        double_same_n = [one, one]
        double_max_min_n = [one, three]
        double_n = [one, two]

        triple_m = [aa, aa, bb]
        triple_mm = [aa, bb, bb]
        triple_n = [one, one, three]

        # f: score_answers(Question, List[Answer]) -> float
        # find similarity of every possible combinations and take avg
        # one valid answer -> 1.0
        homo = HomogeneousCriterion()

        assert homo.score_answers(multiple, single_m) == 1.0
        assert homo.score_answers(multiple, double_same_m) == 1.0
        assert homo.score_answers(multiple, double_diff_m) == 0.0
        assert homo.score_answers(multiple, triple_m) == 0.3333333333333333
        assert homo.score_answers(multiple, triple_mm) == 0.3333333333333333

        assert homo.score_answers(numeric, single_n) == 1.0
        assert homo.score_answers(numeric, double_same_n) == 1.0
        assert homo.score_answers(numeric, double_max_min_n) == 0.0
        assert homo.score_answers(numeric, double_n) == 0.5
        assert homo.score_answers(numeric, triple_n) == 0.3333333333333333


class TestHeterogeneousCriterion:
    def test_isinstance(self) -> None:
        c = HeterogeneousCriterion()
        assert isinstance(c, Criterion)
        assert isinstance(c, type(HomogeneousCriterion()))

    def test_score_answers_hetero(self) -> None:
        numeric = NumericQuestion(2, 'A number bt. 1 and 3 (inclusive)', 1, 3)

        _min = Answer(1)
        _max = Answer(3)
        no = Answer(0)

        single_invalid = [no]
        invalid = [_max, no]
        single = [_min]
        valid = [_min, _max]
        complex_valid = valid + [Answer(2)]

        try:  # single but invalid
            HeterogeneousCriterion.score_answers(
                HeterogeneousCriterion, numeric, single_invalid)
        except InvalidAnswerError:
            pass
        try:  # multiple contain invalid
            HeterogeneousCriterion.score_answers(
                HeterogeneousCriterion, numeric, invalid)
        except InvalidAnswerError:
            pass

        # single and valid
        assert HeterogeneousCriterion.score_answers(
            HeterogeneousCriterion, numeric, single) == 0.0

        # multiple and valid
        assert HeterogeneousCriterion.score_answers(
            HeterogeneousCriterion, numeric, valid) == 1.0
        assert HeterogeneousCriterion.score_answers(
            HeterogeneousCriterion, numeric,
            complex_valid) == 0.6666666666666667

    def test_heterogeneous_criterion_class(self) -> None:
        # question
        yesno = YesNoQuestion(33, 'T or F')
        check = CheckboxQuestion(11, 'A or B', ['A', 'B'])

        # answer
        t = Answer(True)
        f = Answer(False)
        a = Answer(['A'])
        b = Answer(['B'])
        ab = Answer(['A', 'B'])

        # answers
        single_yn = [t]
        double_same_yn = [t, t]
        double_diff_yn = [t, f]
        triple_yn = [t, t, f]

        single_check = [a]
        double_same_check = [a, a]
        double_diff_check = [a, b]
        double_check = [a, ab]
        triple_check = [a, a, b]
        triple_check2 = [a, a, ab]

        # f: score_answers(Question, List[Answer]) -> float
        # 1.0 - similarity
        # one valid answer -> 0.0
        hetero = HeterogeneousCriterion()

        assert hetero.score_answers(yesno, single_yn) == 0.0
        assert hetero.score_answers(yesno, double_same_yn) == 0.0
        assert hetero.score_answers(yesno, double_diff_yn) == 1.0
        assert hetero.score_answers(yesno, triple_yn) == 1 - 1 / 3

        assert hetero.score_answers(check, single_check) == 0.0
        assert hetero.score_answers(check, double_same_check) == 0.0
        assert hetero.score_answers(check, double_diff_check) == 1.0
        assert hetero.score_answers(check, double_check) == 0.5
        assert hetero.score_answers(check, triple_check) == 1 - 1 / 3
        assert hetero.score_answers(check, triple_check2) == 1 - 2 / 3


class TestLonelyMemberCriterion:
    def test_isinstance(self) -> None:
        c = LonelyMemberCriterion()
        assert isinstance(c, Criterion)

    def test_score_answers_lonely(self) -> None:
        numeric = NumericQuestion(2, 'A number bt. 1 and 3 (inclusive)', 1, 3)
        _min = Answer(1)
        _max = Answer(3)
        no = Answer(0)

        single = [_min]
        unique = [_min, _max]
        unique2 = [_max, _max, _min, _max]
        identical = [_min, _min]
        invalid = [no, _max]

        assert LonelyMemberCriterion.score_answers(
            LonelyMemberCriterion, numeric, single) == 0
        assert LonelyMemberCriterion.score_answers(
            LonelyMemberCriterion, numeric, unique) == 0
        assert LonelyMemberCriterion.score_answers(
            LonelyMemberCriterion, numeric, unique2) == 0
        assert LonelyMemberCriterion.score_answers(
            LonelyMemberCriterion, numeric, identical) == 1.0
        try:
            LonelyMemberCriterion.score_answers(
                LonelyMemberCriterion, numeric, invalid)
        except InvalidAnswerError:
            pass

    def test_lonelymember_criterion_class(self) -> None:
        # question
        yesno = YesNoQuestion(33, 'T or F')

        # answer
        t = Answer(True)
        f = Answer(False)

        # answers
        single = [t]
        double_same = [t, t]
        double_diff = [t, f]
        triple1 = [t, t, t]
        triple12 = [t, t, f]
        triple123 = [t, f, f]

        # f: score_answers(Question, List[Answer]) -> float
        # any unique (no identical content w/ others) answer -> 0, else -> 1.0
        # any invalid answer -> InvalidAnswerError
        lonely = LonelyMemberCriterion()

        assert lonely.score_answers(yesno, single) == 0.0
        assert lonely.score_answers(yesno, double_same) == 1.0
        assert lonely.score_answers(yesno, double_diff) == 0.0
        assert lonely.score_answers(yesno, triple1) == 1.0
        assert lonely.score_answers(yesno, triple12) == 0.0
        assert lonely.score_answers(yesno, triple123) == 0.0


class TestGroup:
    def test_length_group(self) -> None:
        g = Group([Student(1, 'Sandy')])
        assert len(g) == 1
        g = Group([Student(1, 'Sandy'),
                   Student(11, 'Cindy'), Student(111, 'Luke')])
        assert len(g) == 3

    def test_contains_group(self) -> None:
        g = Group([Student(1, 'Sandy'),
                   Student(11, 'Cindy'), Student(111, 'Luke')])
        assert Student(1, 'Sandy') in g
        assert Student(2, 'Sandy') not in g

    def test_string_group(self) -> None:
        g = Group([Student(1, 'Sandy'), Student(11, 'Cindy')])
        assert str(g) == 'Sandy Cindy '

    def test_get_members_group(self) -> None:
        students = [Student(1, 'Sandy'), Student(11, 'Cindy')]
        g = Group(students)
        for student in students:
            assert student in g

        assert g._members == students
        assert id(g._members) != id(g.get_members())
        assert str(g.get_members()[0]) == 'Sandy'
        assert str(g.get_members()[1]) == 'Cindy'

    def test_group_class(self) -> None:
        amy = Student(1, 'Amy')
        luke = Student(2, 'Luke')
        amy2 = Student(0, 'Amy')

        students = [amy, luke]
        group = Group(students)

        # f: len -> int
        assert len(group) == 2

        # f: contains -> bool
        assert amy in group
        assert luke in group
        assert amy2 not in group

        # f: str -> str
        assert str(group) == 'Amy Luke '

        assert group._members == students
        assert id(group._members) == id(students)

        # f: get_members() -> List[Student]
        assert group.get_members() == students
        assert id(group.get_members()) != id(students)
        assert group.get_members()[0] == amy
        assert group.get_members()[1] == luke


class TestGrouping:
    def test_length_grouping(self) -> None:
        students1 = [Student(1, 'Sandy'), Student(11, 'Cindy')]
        students2 = [Student(2, 'Leo'), Student(22, 'Luke')]
        group1 = Group(students1)
        group2 = Group(students2)
        grouping = Grouping()
        grouping.add_group(group1)
        assert len(grouping) == 1
        grouping.add_group(group2)
        assert len(grouping) == 2

    def test_string_grouping(self) -> None:
        students1 = [Student(1, 'Sandy'), Student(11, 'Cindy')]
        students2 = [Student(2, 'Leo'), Student(22, 'Luke')]
        group1 = Group(students1)
        group2 = Group(students2)
        grouping = Grouping()
        grouping.add_group(group1)
        grouping.add_group(group2)
        assert str(grouping) == 'Sandy Cindy \nLeo Luke \n'

    def test_add_group(self) -> None:
        sandy = Student(1, 'Sandy')
        cindy = Student(11, 'Cindy')
        leo = Student(2, 'Leo')
        luke = Student(22, 'Luke')
        ben = Student(3, 'Ben')

        emp = Group([])  # an empty group violates the representation invariant
        valid = Group([cindy, leo])
        single = Group([luke])
        single_dup = Group([sandy, luke])  # a group with one duplicate student
        invalid = Group([ben, ben])  # a group with self duplicate

        g = Grouping()
        assert not g.add_group(emp)
        assert g.add_group(valid)
        assert g.add_group(single)
        assert not g.add_group(single_dup)
        assert not g.add_group(invalid)

    def test_get_groups_grouping(self) -> None:
        g = Grouping()
        sandy = Student(1, 'Sandy')
        cindy = Student(11, 'Cindy')
        leo = Student(2, 'Leo')
        luke = Student(22, 'Luke')
        group = Group([cindy, sandy])
        group2 = Group([leo, luke])
        g.add_group(group)
        g.add_group(group2)

        for group in g.get_groups():
            for member in group.get_members():
                assert member in group or member in group2

        assert id(g._groups) != id(g.get_groups())

    def test_grouping_class(self) -> None:
        amy = Student(1, 'Amy')
        luke = Student(2, 'Luke')
        nick = Student(3, 'Nick')
        ben = Student(4, 'Ben')

        group1 = Group([amy, luke])
        group2 = Group([nick])
        invalid = Group([amy, ben])

        grouping = Grouping()

        # f: len -> int
        assert len(grouping) == 0

        # f: str -> str
        assert str(grouping) == ''

        # f: add_group(Group) -> bool
        assert grouping.add_group(group1)
        assert grouping.add_group(group2)
        assert not grouping.add_group(invalid)
        assert not grouping.add_group(Group([]))

        assert len(grouping) == 2
        assert str(grouping) == 'Amy Luke \nNick \n'

        # f: get_members() -> List[Student]
        assert grouping._groups == grouping.get_groups()
        assert id(grouping._groups) != id(grouping.get_groups())
        assert group1 in grouping.get_groups()
        assert group2 in grouping.get_groups()


# No two questions on this survey have the same id
# Each key in _questions equals the id attribute of its value
# Each key in _criteria occurs as a key in _questions
# Each key in _weights occurs as a key in _questions
# Each value in _weights is greater than 0
# _default_weight > 0
class TestSurvey:
    def test_length_survey(self) -> None:
        numeric = NumericQuestion(1, 'Pick a number from 1-3 (inclusive)', 1, 3)
        numeric2 = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1,
                                   3)

        single = [numeric]  # single
        dup = [numeric, numeric]  # duplicated
        more = [numeric, numeric2]  # no duplicate

        assert len(Survey(single)) == len(Survey(dup))
        assert len(Survey(more)) == 2

    def test_contain_survey(self) -> None:
        numeric = NumericQuestion(1, 'Pick a number from 1-3 (inclusive)', 1, 3)
        numeric2 = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)',
                                   1, 3)
        single = [numeric]

        assert numeric in Survey(single)
        assert numeric2 not in Survey(single)

    def test_string_survey(self) -> None:
        multiple = MultipleChoiceQuestion(1, 'Which is peach?',
                                          ['A. peach', 'B. banana'])
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        yesno = YesNoQuestion(3, 'Are people crazy?')
        check = CheckboxQuestion(4, 'Which of them can be red?',
                                 ['A. apple', 'B. cherry', 'C. banana'])

        variety = [multiple, numeric, yesno, check]
        assert str(Survey(variety)) == (str(multiple) + '\n' +
                                        str(numeric) + '\n' +
                                        str(yesno) + '\n' +
                                        str(check) + '\n')

    def test_get_question_survey(self) -> None:
        multiple = MultipleChoiceQuestion(1, 'Which is peach?',
                                          ['A. peach', 'B. banana'])
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        yesno = YesNoQuestion(3, 'Are people crazy?')
        check = CheckboxQuestion(4, 'Which of them can be red?',
                                 ['A. apple', 'B. cherry', 'C. banana'])

        variety = [multiple, numeric, yesno, check]
        s = Survey(variety)
        assert s.get_questions() == variety

    def test__get_criterion_survey(self) -> None:
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        yesno = YesNoQuestion(3, 'Are people crazy?')

        variety = [numeric, yesno]
        s = Survey(variety)
        assert isinstance(s._get_criterion(numeric), Criterion)
        assert isinstance(s._get_criterion(yesno), Criterion)
        assert s.set_criterion(LonelyMemberCriterion(), numeric)
        # assert isinstance(s._get_criterion(numeric), Criterion)

    def test__get_weight_survey(self) -> None:
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        yesno = YesNoQuestion(3, 'Are people crazy?')

        variety = [numeric, yesno]
        s = Survey(variety)
        assert s._get_weight(numeric) == 1
        s.set_weight(0.5, numeric)
        assert s._get_weight(yesno) == 1
        assert s._get_weight(numeric) == 0.5

    def test_set_weight_survey(self) -> None:
        multiple = MultipleChoiceQuestion(1, 'Which is peach?',
                                          ['A. peach', 'B. banana'])
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        yesno = YesNoQuestion(3, 'Are people crazy?')
        check = CheckboxQuestion(4, 'Which of them can be red?',
                                 ['A. apple', 'B. cherry', 'C. banana'])
        excluded = YesNoQuestion(0, 'Am I excluded?')

        variety = [multiple, numeric, yesno, check]
        s = Survey(variety)

        # if question.id not in survey
        assert not s.set_weight(1, excluded)

        assert s.set_weight(0.5, numeric)
        assert s._get_weight(numeric) == 0.5

    def test_set_criterion_survey(self) -> None:
        multiple = MultipleChoiceQuestion(1, 'Which is peach?',
                                          ['A. peach', 'B. banana'])
        numeric = NumericQuestion(2, 'Pick a number from 1-3 (inclusive)', 1, 3)
        yesno = YesNoQuestion(3, 'Are people crazy?')
        check = CheckboxQuestion(4, 'Which of them can be red?',
                                 ['A. apple', 'B. cherry', 'C. banana'])
        excluded = YesNoQuestion(0, 'Am I excluded?')

        variety = [multiple, numeric, yesno, check]
        s = Survey(variety)

        # if question.id not in survey
        assert not s.set_criterion(LonelyMemberCriterion(), excluded)
        assert s.set_criterion(LonelyMemberCriterion(), numeric)
        assert isinstance(s._get_criterion(numeric), Criterion)

    def test_score_students_survey(self) -> None:
        yesno = YesNoQuestion(3, 'Are people crazy?')
        questions = [yesno]

        lisa = Student(1, 'Lisa')
        bob = Student(2, 'Bob')
        caro = Student(3, 'Caro')
        milly = Student(4, 'Milly')

        lisa.set_answer(yesno, Answer(True))
        bob.set_answer(yesno, Answer(True))
        milly.set_answer(yesno, Answer(False))
        caro.set_answer(yesno, Answer('Ha?'))  # invalid answer

        single = [bob]
        double = [lisa, bob]  # same answer
        triple = [lisa, bob, milly]  # more and different answer
        nah = [lisa, caro]

        s = Survey([])
        assert s.score_students(single) == 0  # if empty

        s = Survey(questions)
        assert s.score_students(nah) == 0  # if InvalidAnswerError

        # set by default: homo and 1
        assert s.score_students(single) == 1.0
        assert s.score_students(double) == 1.0
        assert s.score_students(triple) == 0.3333333333333333

        # weight: 0.5
        for question in s.get_questions():
            s.set_weight(0.5, question)
        assert s.score_students(single) == 0.5
        assert s.score_students(double) == 0.5
        assert s.score_students(triple) == 0.3333333333333333 * 0.5

        # criteria: hetero
        for question in s.get_questions():
            s.set_criterion(HeterogeneousCriterion(), question)
        assert s.score_students(single) == 0
        assert s.score_students(double) == 0
        assert s.score_students(triple) == 0.33333333333333337

    def test_score_grouping_survey(self) -> None:
        yesno = YesNoQuestion(3, 'Are people crazy?')
        questions = [yesno]

        lisa = Student(1, 'Lisa')
        lisa2 = Student(12, 'Lisa')
        bob = Student(2, 'Bob')
        bob2 = Student(22, 'Bob')
        bob3 = Student(223, 'Bob')
        caro = Student(3, 'Caro')
        milly = Student(4, 'Milly')

        lisa.set_answer(yesno, Answer(True))
        lisa2.set_answer(yesno, Answer(True))
        bob.set_answer(yesno, Answer(True))
        bob2.set_answer(yesno, Answer(True))
        bob3.set_answer(yesno, Answer(True))
        milly.set_answer(yesno, Answer(False))
        caro.set_answer(yesno, Answer('Ha?'))  # invalid answer

        invalid = Group([caro])
        single = Group([bob])
        double = Group([lisa, bob2])  # same answer
        triple = Group([lisa2, bob3, milly])  # more and different answer

        s = Survey(questions)

        grouping = Grouping()
        assert s.score_grouping(grouping) == 0.0  # if empty
        grouping.add_group(invalid)
        assert s.score_grouping(grouping) == 0.0  # if InvalidAnswerError

        single_grouping = Grouping()
        assert single_grouping.add_group(single)
        assert single_grouping.get_groups()[0] == single
        assert single.get_members()[0] == bob
        assert s.score_students(single.get_members()) == 1.0
        assert s.score_grouping(single_grouping) == 1.0

        double_grouping = Grouping()
        double_grouping.add_group(double)
        assert s.score_grouping(double_grouping) == 1.0
        double_grouping.add_group(single)
        assert s.score_grouping(double_grouping) == 1.0

        triple_grouping = Grouping()
        triple_grouping.add_group(triple)
        assert s.score_grouping(triple_grouping) == 0.3333333333333333
        triple_grouping.add_group(double)
        assert s.score_grouping(triple_grouping) == 0.6666666666666666
        triple_grouping.add_group(single)
        assert s.score_grouping(triple_grouping) == 0.7777777777777777

    def test_score_grouping_survey_2(self) -> None:
        # students
        duke = Student(1, 'Duke')
        kari = Student(2, 'Kari')
        larry = Student(3, 'Larry')
        ben = Student(4, 'Ben')

        # questions
        # same = 1.0, diff = 0.0
        multi = MultipleChoiceQuestion(11, 'A or B', ['A', 'B'])
        # 1.0 - abs(answer1 - answer2) / (self._max - self._min)
        num = NumericQuestion(22, '1-3', 1, 3)
        # same = 1.0, diff = 0.0
        yesno = YesNoQuestion(33, 'True or False')
        # common / unique
        check = CheckboxQuestion(44, 'A or B', ['A', 'B'])

        # answers
        a = Answer('A')
        b = Answer('B')
        assert multi.validate_answer(a)
        assert multi.validate_answer(b)

        one = Answer(1)
        three = Answer(3)
        assert num.validate_answer(one)
        assert num.validate_answer(three)

        t = Answer(True)
        f = Answer(False)
        assert yesno.validate_answer(t)
        assert yesno.validate_answer(f)

        aa = Answer(['A'])
        bb = Answer(['B'])
        assert check.validate_answer(aa)
        assert check.validate_answer(bb)
        assert check.get_similarity(aa, bb) == 0

        # set answers
        duke.set_answer(multi, a)
        kari.set_answer(multi, a)
        larry.set_answer(multi, a)
        ben.set_answer(multi, b)

        duke.set_answer(num, one)
        kari.set_answer(num, one)
        larry.set_answer(num, one)
        ben.set_answer(num, three)

        duke.set_answer(yesno, t)
        kari.set_answer(yesno, t)
        larry.set_answer(yesno, t)
        ben.set_answer(yesno, f)

        duke.set_answer(check, aa)
        kari.set_answer(check, aa)
        larry.set_answer(check, aa)
        ben.set_answer(check, bb)

        # make survey
        survey = Survey([multi, num, yesno, check])

        # make lists of students
        best = [duke, kari]  # m: 1, n: 1, y: 1, c: 1
        worst = [larry, ben]  # m: 0, n: 0, y: 0, c: 0.5
        assert survey.score_students(best) == 1.0
        assert survey.score_students(worst) == 0

        best_group = Group([duke, kari])
        worst_group = Group([larry, ben])

        # make grouping
        grouping = Grouping()
        grouping.add_group(best_group)
        grouping.add_group(worst_group)

        assert survey.score_grouping(grouping) == 0.5

    def test_survey_class(self) -> None:
        # questions and answers
        multiple = MultipleChoiceQuestion(11, 'A or B', ['A', 'B'])
        clone_multiple = MultipleChoiceQuestion(11, 'C or D', ['C', 'D'])
        aa = Answer('A')
        bb = Answer('B')

        numeric = NumericQuestion(22, '1-3', 1, 3)
        one = Answer(1)
        two = Answer(2)
        three = Answer(3)

        yesno = YesNoQuestion(33, 'T or F')
        t = Answer(True)
        f = Answer(False)

        check = CheckboxQuestion(44, 'A or B', ['A', 'B'])
        a = Answer(['A'])
        b = Answer(['B'])

        dne = NumericQuestion(00, 'Hey', 0, 0)

        survey = Survey([multiple, numeric, yesno, check, multiple])
        assert survey._questions == {11: multiple, 22: numeric,
                                     33: yesno, 44: check}
        assert survey._criteria == {}
        assert survey._weights == {}
        assert survey._default_weight == 1
        assert isinstance(survey._default_criterion, Criterion)
        assert isinstance(survey._default_criterion,
                          type(HomogeneousCriterion()))

        # f: len -> int
        empty = Survey([])
        assert len(empty) == 0
        assert len(survey) == 4
        assert multiple in survey
        assert clone_multiple in survey
        assert numeric in survey
        assert yesno in survey
        assert check in survey

        # f: contains -> bool
        assert dne not in survey
        for question in survey.get_questions():
            assert question in survey

        # f: str -> str
        assert str(survey) == (str(multiple) + '\n' + str(numeric) +
                               '\n' + str(yesno) + '\n' + str(check) + '\n')

        # f: get_questions() -> List[Questions]
        assert survey.get_questions() == [multiple, numeric, yesno, check]

        # f: _get_criterion(Question) -> Criterion
        assert isinstance(HomogeneousCriterion(), Criterion)
        assert isinstance(survey._get_criterion(multiple), Criterion)

        for question in survey.get_questions():
            assert isinstance(survey._get_criterion(question),
                              HomogeneousCriterion)

        # f: _get_weight(Question) -> int
        for question in survey.get_questions():
            assert isinstance(survey._get_weight(question), int)
            assert survey._get_weight(question) == 1

        # f: set_weight(int, Question) -> bool
        assert survey._weights == {}
        assert not survey.set_weight(0, multiple)
        assert not survey.set_weight(-1, numeric)
        assert not survey.set_weight(1, dne)  # dne is not in survey
        for question in survey.get_questions():
            assert survey.set_weight(1, question)
            assert survey._get_weight(question) == 1
        assert survey._weights == {11: 1, 22: 1, 33: 1, 44: 1}

        # f: set_criterion(Criterion, Question) -> bool
        assert survey._criteria == {}
        assert not survey.set_criterion(HomogeneousCriterion, dne)
        for question in survey.get_questions():
            assert survey.set_criterion(HeterogeneousCriterion(), question)
            assert isinstance(survey._get_criterion(question),
                              HeterogeneousCriterion)

        # f: score_students(List[Student]) -> float
        # not question or InvalidAnswerError -> 0.0
        # for each question, criteria.score_answers(question, answers) / # of s
        empty = Survey([])

        # students
        ribosome = Student(1, 'Ribosome')
        nucleus = Student(2, 'Nucleus')
        prokaryote = Student(3, 'Prokaryote')
        eukaryote = Student(4, 'Eukaryote')
        cytoplasm = Student(0, 'Cytoplasm')

        # set answers
        ribosome.set_answer(multiple, aa)
        nucleus.set_answer(multiple, aa)
        prokaryote.set_answer(multiple, bb)
        eukaryote.set_answer(multiple, bb)
        cytoplasm.set_answer(multiple, a)  # invalid answer

        ribosome.set_answer(numeric, one)
        nucleus.set_answer(numeric, one)
        prokaryote.set_answer(numeric, three)
        eukaryote.set_answer(numeric, three)
        cytoplasm.set_answer(numeric, two)

        ribosome.set_answer(yesno, t)
        nucleus.set_answer(yesno, t)
        prokaryote.set_answer(yesno, f)
        eukaryote.set_answer(yesno, f)
        cytoplasm.set_answer(yesno, t)

        ribosome.set_answer(check, a)
        nucleus.set_answer(check, a)
        prokaryote.set_answer(check, b)
        eukaryote.set_answer(check, b)
        cytoplasm.set_answer(check, a)

        # list of students
        invalid = [cytoplasm, ribosome]
        single = [prokaryote]
        same = [prokaryote, eukaryote]
        diff = [ribosome, prokaryote]
        complicated = [prokaryote, eukaryote, ribosome, nucleus]

        # HeterogeneousCriterion
        assert survey.score_students(invalid) == 0.0  # invalid answer
        assert empty.score_students(single) == 0.0  # no question
        assert survey.score_students(single) == 0.0
        assert survey.score_students(same) == 0.0
        assert survey.score_students(diff) == 1.0
        assert survey.score_students(complicated) == 1 - 1 / 3

        # HomogeneousCriterion
        for question in survey.get_questions():
            assert survey.set_criterion(HomogeneousCriterion(), question)
            assert isinstance(survey._get_criterion(question),
                              HomogeneousCriterion)

        assert survey.score_students(invalid) == 0.0  # invalid answer
        assert empty.score_students(single) == 0.0  # no question
        assert survey.score_students(single) == 1.0
        assert survey.score_students(same) == 1.0
        assert survey.score_students(diff) == 0.0
        assert survey.score_students(complicated) == 1 / 3

        # score_grouping(Grouping) -> float
        # no group / InvalidAnswerError -> 0.0
        # score of groups / number of groups

        # lists of students
        invalid = [cytoplasm, ribosome]
        same = [prokaryote, eukaryote]
        diff = [ribosome, prokaryote]
        complicated = [prokaryote, eukaryote, ribosome, nucleus]

        # groups
        invalid_group = Group(invalid)

        # grouping
        grouping = Grouping()
        invalid_grouping = Grouping()
        invalid_grouping.add_group(invalid_group)

        assert survey.score_grouping(grouping) == 0.0
        assert survey.score_grouping(invalid_grouping) == 0.0

        cytoplasm.set_answer(multiple, bb)
        single = [cytoplasm]
        single_group = Group(single)
        same_group = Group(same)
        diff_group = Group(diff)
        complicated_group = Group(complicated)

        grouping.add_group(single_group)
        assert survey.score_grouping(grouping) == 1.0
        grouping.add_group(same_group)
        assert survey.score_grouping(grouping) == 1.0

        grouping = Grouping()
        grouping.add_group(single_group)
        assert survey.score_grouping(grouping) == 1.0
        grouping.add_group(diff_group)
        assert survey.score_grouping(grouping) == 0.5

        grouping = Grouping()
        grouping.add_group(complicated_group)
        assert survey.score_grouping(grouping) == 1 / 3
        grouping.add_group(single_group)
        assert survey.score_grouping(grouping) == (1 / 3 + 1) / 2


class TestHelperFunctions:
    def test_slice_list(self) -> None:
        # lists
        single = [1]
        double = [1, 2]
        triple = [1, 2, 3]
        four = [1, 2, 3, 4]
        more = [1, 2, 3, 4, 5, 6, 7, 8]

        assert slice_list(single, 1) == [[1]]
        assert slice_list(double, 1) == [[1], [2]]
        assert slice_list(double, 2) == [[1, 2]]
        assert slice_list(triple, 3) == [[1, 2, 3]]
        assert slice_list(triple, 2) == [[1, 2], [3]]
        assert slice_list(four, 2) == [[1, 2], [3, 4]]
        assert slice_list(four, 3) == [[1, 2, 3], [4]]
        assert slice_list(more, 3) == [[1, 2, 3], [4, 5, 6], [7, 8]]
        assert slice_list(more, 5) == [[1, 2, 3, 4, 5], [6, 7, 8]]

    def test_windows(self) -> None:
        # lists
        single = [1]
        double = [1, 2]
        triple = [1, 2, 3]
        four = [1, 2, 3, 4]
        more = [1, 2, 3, 4, 5, 6, 7, 8]

        assert windows(single, 1) == [[1]]
        assert windows(double, 1) == [[1], [2]]
        assert windows(double, 2) == [[1, 2]]
        assert windows(triple, 3) == [[1, 2, 3]]
        assert windows(triple, 2) == [[1, 2], [2, 3]]
        assert windows(four, 2) == [[1, 2], [2, 3], [3, 4]]
        assert windows(four, 3) == [[1, 2, 3], [2, 3, 4]]
        assert windows(more, 5) == [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6],
                                    [3, 4, 5, 6, 7], [4, 5, 6, 7, 8]]


class TestAlphaGrouper:
    def test_isinstance(self) -> None:
        g = AlphaGrouper(2)
        assert isinstance(g, Grouper)

    def test_make_grouping_alpha(self) -> None:
        paul = Student(1, 'Paul')
        lily = Student(2, 'Lily')
        chris = Student(3, 'Chris')
        icy = Student(4, 'Icy')
        course = Course('Swimming')
        course.enroll_students([chris, lily, icy, paul])

        s = Survey([])

        group = AlphaGrouper(2)
        grouping = group.make_grouping(course, s)
        assert isinstance(grouping, Grouping)
        assert str(grouping.get_groups()[0].get_members()[0]) == 'Chris'
        assert str(grouping.get_groups()[0].get_members()[1]) == "Icy"
        assert str(grouping.get_groups()[1].get_members()[0]) == "Lily"
        assert str(grouping.get_groups()[1].get_members()[1]) == "Paul"

        group2 = AlphaGrouper(3)
        grouping = group2.make_grouping(course, s)
        assert isinstance(grouping, Grouping)
        assert str(grouping.get_groups()[0].get_members()[0]) == 'Chris'
        assert str(grouping.get_groups()[0].get_members()[1]) == "Icy"
        assert str(grouping.get_groups()[0].get_members()[2]) == "Lily"
        assert str(grouping.get_groups()[1].get_members()[0]) == "Paul"


class TestRandomGrouper:
    def test_isinstance(self) -> None:
        g = RandomGrouper(2)
        assert isinstance(g, Grouper)

    def test_make_grouping_randomly(self) -> None:
        paul = Student(1, 'Paul')
        lily = Student(2, 'Lily')
        chris = Student(3, 'Chris')
        icy = Student(4, 'Icy')
        course = Course('Swimming')
        course.enroll_students([chris, lily, icy, paul])

        s = Survey([])

        group = RandomGrouper(2)
        grouping = group.make_grouping(course, s)

        assert isinstance(grouping, Grouping)
        assert len(grouping.get_groups()) == 2
        assert (
                (str(grouping.get_groups()[0].get_members()[0]) != 'Chris') or
                (str(grouping.get_groups()[0].get_members()[1]) != "Lily") or
                (str(grouping.get_groups()[1].get_members()[0]) != "Icy") or
                (str(grouping.get_groups()[1].get_members()[1]) != "Paul"))

        group2 = RandomGrouper(3)
        grouping = group2.make_grouping(course, s)
        assert isinstance(grouping, Grouping)
        assert len(grouping.get_groups()) == 2
        assert ((str(grouping.get_groups()[0].get_members()[0]) != 'Chris') or
                (str(grouping.get_groups()[0].get_members()[1]) != "Lily") or
                (str(grouping.get_groups()[0].get_members()[2]) != "Icy") or
                (str(grouping.get_groups()[1].get_members()[0]) != "Paul"))


class TestGreedyGrouper:
    def test_doctest__best_match(self) -> None:
        amy = Student(1, 'Amy')
        lisa = Student(2, 'Lisa')
        kali = Student(3, 'Kali')
        may = Student(4, 'May')
        q = YesNoQuestion(0, 'True or False')
        two = GreedyGrouper(2)
        s = Survey([q])
        amy.set_answer(q, Answer(True))
        lisa.set_answer(q, Answer(True))
        kali.set_answer(q, Answer(False))
        may.set_answer(q, Answer(True))
        assert two._best_match(s, [amy, lisa, kali], [amy]) == [amy, lisa]
        assert two._best_match(s, [amy, lisa, kali, may],
                               [amy, lisa]) == [amy, lisa, may]

    def test_make_grouping(self) -> None:
        amy = Student(1, 'Amy')
        lisa = Student(2, 'Lisa')
        kali = Student(3, 'Kali')
        may = Student(4, 'May')

        cooking = Course('Cooking')
        cooking.enroll_students([amy, lisa, kali, may])
        baking = Course('Baking')
        baking.enroll_students([amy, lisa, kali])
        same = Course('Same')
        same.enroll_students([amy, lisa])
        diff = Course('Diff')
        diff.enroll_students([amy, kali])

        q = YesNoQuestion(0, 'True or False')
        amy.set_answer(q, Answer(True))
        lisa.set_answer(q, Answer(True))
        kali.set_answer(q, Answer(False))
        may.set_answer(q, Answer(True))

        s = Survey([q])
        two = GreedyGrouper(2)

        # isinstance Grouping
        g_grouping = two.make_grouping(cooking, s)
        assert isinstance(g_grouping, Grouping)
        g_grouping2 = two.make_grouping(baking, s)
        assert isinstance(g_grouping2, Grouping)

        same_grouping = two.make_grouping(same, s)
        diff_grouping = two.make_grouping(diff, s)

        groups1 = g_grouping.get_groups()  # a list of group
        assert len(groups1[0]) == 2
        assert len(groups1[1]) == 2

        groups2 = g_grouping2.get_groups()
        assert len(groups2[0]) == 2
        assert len(groups2[1]) == 1

        group_same = same_grouping.get_groups()
        assert len(group_same) == 1
        group_diff = diff_grouping.get_groups()
        assert len(group_diff) == 1

        members11 = groups1[0].get_members()
        members12 = groups1[1].get_members()
        assert members11[0] == amy
        assert members11[1] == lisa
        assert members12[0] == kali
        assert members12[1] == may

        members21 = groups2[0].get_members()
        members22 = groups2[1].get_members()
        assert members21[0] == amy
        assert members21[1] == lisa
        assert members22[0] == kali

        same_members = group_same[0].get_members()
        diff_members = group_diff[0].get_members()
        assert same_members[0] == amy
        assert same_members[1] == lisa
        assert diff_members[0] == amy
        assert diff_members[1] == kali


class TestWindowGrouper:
    def test_make_grouping(self) -> None:
        lily = Student(1, 'Lily')
        mike = Student(2, 'Mike')
        coco = Student(3, 'Coco')

        yesno = YesNoQuestion(0, 'Yeah?')
        survey = Survey([yesno])
        students = [lily, mike]
        for student in students:
            student.set_answer(yesno, Answer(True))
        coco.set_answer(yesno, Answer(False))

        students = students + [coco]
        course = Course('course')
        course.enroll_students(students)

        assert windows(students, 2) == [[lily, mike], [mike, coco]]
        assert survey.score_students([lily, mike]) == 1.0
        assert survey.score_students([mike, coco]) == 0.0
        window_g = WindowGrouper(2)
        grouping = window_g.make_grouping(course, survey)
        assert isinstance(grouping, Grouping)
        assert grouping.get_groups()[0].get_members()[0] == lily
        assert grouping.get_groups()[0].get_members()[1] == mike
        assert grouping.get_groups()[1].get_members()[0] == coco

    def test_doctest__find_best_window(self) -> None:
        lily = Student(1, 'Lily')
        mike = Student(2, 'Mike')
        coco = Student(3, 'Coco')
        yesno = YesNoQuestion(0, 'Yeah?')
        survey = Survey([yesno])
        lily.set_answer(yesno, Answer(True))
        mike.set_answer(yesno, Answer(True))
        coco.set_answer(yesno, Answer(False))
        students = [lily, mike, coco]
        window_g = WindowGrouper(2)
        assert window_g._find_best_window(
            windows(students, 2), survey) == [lily, mike]


if __name__ == '__main__':
    pytest.main(['tests.py'])
