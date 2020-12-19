"""CSC148 Assignment 1

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Misha Schwartz, Mario Badr, Christine Murad, Diane Horton, Sophia Huynh
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) 2020 Misha Schwartz, Mario Badr, Christine Murad, Diane Horton,
Sophia Huynh and Jaisie Sin

=== Module Description ===

This file contains classes that define different algorithms for grouping
students according to chosen criteria and the group members' answers to survey
questions. This file also contain a classe that describes a group of students as
well as a grouping (a group of groups).
"""
from __future__ import annotations
import random
from typing import TYPE_CHECKING, List, Any, Optional
from course import Course, Student, sort_students

if TYPE_CHECKING:
    from survey import Survey, Question, YesNoQuestion, Answer


def slice_list(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing slices of <lst> in order. Each slice is a
    list of size <n> containing the next <n> elements in <lst>.

    The last slice may contain fewer than <n> elements in order to make sure
    that the returned list contains all elements in <lst>.

    === Precondition ===
    n <= len(lst)

    >>> slice_list([3, 4, 6, 2, 3], 2) == [[3, 4], [6, 2], [3]]
    True
    >>> slice_list(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [False]]
    True
    """
    i = 0
    sliced = []
    while i < len(lst):
        sliced.append(lst[i: i + n])
        i += n
    return sliced


def windows(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing windows of <lst> in order. Each window is a list
    of size <n> containing the elements with index i through index i+<n> in the
    original list where i is the index of window in the returned list.

    === Precondition ===
    n <= len(lst)

    >>> windows([3, 4, 6, 2, 3], 2) == [[3, 4], [4, 6], [6, 2], [2, 3]]
    True
    >>> windows(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [1, 6.0, False]]
    True
    """
    i = 0
    window = []
    while i < len(lst) and i + n < len(lst) + 1:
        window.append(lst[i: i + n])
        i += 1
    return window


class Grouper:
    """
    An abstract class representing a grouper used to create a grouping of
    students according to their answers to a survey.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def __init__(self, group_size: int) -> None:
        """
        Initialize a grouper that creates groups of size <group_size>

        === Precondition ===
        group_size > 1
        """
        self.group_size = group_size

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """ Return a grouping for all students in <course> using the questions
        in <survey> to create the grouping.
        """
        raise NotImplementedError

    def _best_match(self, survey: Survey, all_students: List[Student],
                    ones: List[Student]) -> List[Student]:
        """
        Return a list containing the combination of students that has the
        highest score.
        """
        raise NotImplementedError

    def _find_best_window(self, windows_: List[Student],
                          survey: Survey) -> List[Student]:
        """
        Return a window (a list of student) in the <windows_> that, according to
        survey, has a higher score than the window right after it.
        """
        raise NotImplementedError


class AlphaGrouper(Grouper):
    """
    A grouper that groups students in a given course according to the
    alphabetical order of their names.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        The first group should contain the students in <course> whose names come
        first when sorted alphabetically, the second group should contain the
        next students in that order, etc.

        All groups in this grouping should have exactly self.group_size members
        except for the last group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.

        Hint: the sort_students function might be useful
        """
        grouping = Grouping()
        students = list(course.get_students())
        sorted_s = sort_students(students, 'name')
        sliced_s = slice_list(sorted_s, self.group_size)
        for slices in sliced_s:
            grouping.add_group(Group(slices))
        return grouping

    def _best_match(self, survey: Survey, all_students: List[Student],
                    ones: List[Student]) -> List[Student]:
        """
        Return a list containing the combination of students that has the
        highest score.
        """
        raise NotImplementedError

    def _find_best_window(self, windows_: List[Student],
                          survey: Survey) -> List[Student]:
        """
        Return a window (a list of student) in the <windows_> that, according to
        survey, has a higher score than the window right after it.
        """
        raise NotImplementedError


class RandomGrouper(AlphaGrouper):
    """
    A grouper used to create a grouping of students by randomly assigning them
    to groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Students should be assigned to groups randomly.

        All groups in this grouping should have exactly self.group_size members
        except for one group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.
        """
        grouping = Grouping()
        students = list(course.get_students())
        while len(students) > self.group_size:
            random.shuffle(students)
            sliced = slice_list(students, self.group_size)
            picked = sliced[0]
            grouping.add_group(Group(picked))
            for student in picked:
                students.remove(student)
        if len(students) > 0:
            grouping.add_group(Group(students))
        return grouping

    def _best_match(self, survey: Survey, all_students: List[Student],
                    ones: List[Student]) -> List[Student]:
        """
        Return a list containing the combination of students that has the
        highest score.
        """
        raise NotImplementedError

    def _find_best_window(self, windows_: List[Student],
                          survey: Survey) -> List[Student]:
        """
        Return a window (a list of student) in the <windows_> that, according to
        survey, has a higher score than the window right after it.
        """
        raise NotImplementedError


class GreedyGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a greedy algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. select the first student in the tuple that hasn't already been put
           into a group and put this student in a new group.
        2. select the student in the tuple that hasn't already been put into a
           group that, if added to the new group, would increase the group's
           score the most (or reduce it the least), add that student to the new
           group.
        3. repeat step 2 until there are N students in the new group where N is
           equal to self.group_size.
        4. repeat steps 1-3 until all students have been placed in a group.

        In step 2 above, use the <survey>.score_students method to determine
        the score of each group of students.

        The final group created may have fewer than N members if that is
        required to make sure all students in <course> are members of a group.
        """
        grouping = Grouping()
        students = list(course.get_students())

        # if more groups can be formed
        while len(students) > self.group_size:

            # put the first ungrouped kid in a list
            prepared = [students[0]]

            # if the desired size has not been reached
            while len(prepared) != self.group_size:

                # the length of prepared students should increase one each time
                prepared = self._best_match(survey, students, prepared)

            # after the desired length is reached
            # group the prepared students and put into grouping
            grouping.add_group(Group(prepared))

            # remove the grouped students from the ungrouped list
            for student in prepared:
                students.remove(student)

        # after all possible best_matched groups are formed
        # if there are some students remaining to be ungrouped
        if len(students) > 0:
            grouping.add_group(Group(students))
        return grouping

    def _best_match(self, survey: Survey, all_students: List[Student],
                    ones: List[Student]) -> List[Student]:
        """
        Return a list containing the combination of students that has the
        highest score.
        >>> amy = Student(1, 'Amy')
        >>> lisa = Student(2, 'Lisa')
        >>> kali = Student(3, 'Kali')
        >>> may = Student(4, 'May')
        >>> q = Question(0, 'True or False')
        >>> gg = GreedyGrouper(2)
        >>> s = Survey([q])
        >>> amy.set_answer(q, Answer(True))
        >>> lisa.set_answer(q, Answer(True))
        >>> kali.set_answer(q, Answer(False))
        >>> may.set_answer(q, Answer(True))
        >>> gg._best_match([amy, lisa, kali], [amy])
        [amy, lisa]
        >>> gg._best_match([amy, lisa, kali, may], [amy, lisa])
        [amy, lisa, may]
        """
        # this keeps track of all scores with its owners
        best = {}
        scores = []  # this keeps all the scores

        # for all the students
        for each in all_students:
            # avoid duplicates
            if each not in ones:
                score = survey.score_students(ones + [each])
                scores.append(score)
                # avoid being covered
                if score not in best:
                    best[score] = ones + [each]

        return best[max(scores)]

    def _find_best_window(self, windows_: List[Student],
                          survey: Survey) -> List[Student]:
        """
        Return a window (a list of student) in the <windows_> that, according to
        survey, has a higher score than the window right after it.
        """
        raise NotImplementedError


class WindowGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a window search algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. Get the windows of the list of students who have not already been
           put in a group.
        2. For each window in order, calculate the current window's score as
           well as the score of the next window in the list. If the current
           window's score is greater than or equal to the next window's score,
           make a group out of the students in current window and start again at
           step 1. If the current window is the last window, compare it to the
           first window instead.

        In step 2 above, use the <survey>.score_students to determine the score
        of each window (list of students).

        In step 1 and 2 above, use the windows function to get the windows of
        the list of students.

        If there are any remaining students who have not been put in a group
        after repeating steps 1 and 2 above, put the remaining students into a
        new group.
        """
        # gather a list of ungrouped students
        students = list(course.get_students())
        grouping = Grouping()

        # when more than one group can be formed
        while len(students) > self.group_size:

            # create a (new) window
            split = windows(students, self.group_size)

            # find the window that has a higher mark than the next
            best_window = self._find_best_window(split, survey)

            # add to grouping
            grouping.add_group(Group(best_window))

            # remove all students in that window from ungrouped
            for student in best_window:
                students.remove(student)

        # if there are students remaining
        if len(students) > 0:
            grouping.add_group(Group(students))

        return grouping

    def _find_best_window(self, windows_: List[Student],
                          survey: Survey) -> Optional[List[Student]]:
        """
        Return a window (a list of student) in the <windows_> that, according to
        survey, has a higher score than the window right after it.
        >>> lily = Student(1, 'Lily')
        >>> mike = Student(2, 'Mike')
        >>> coco = Student(3, 'Coco')
        >>> yesno = YesNoQuestion(0, 'Yeah?')
        >>> survey = Survey([yesno])
        >>> lily.set_answer(yesno, Answer(True))
        >>> mike.set_answer(yesno, Answer(True))
        >>> coco.set_answer(yesno, Answer(False))
        >>> students = [lily, mike, coco]
        >>> window_g = WindowGrouper(2)
        >>> window_g._find_best_window(windows(students), survey)
        [lily, mike]
        """
        i = 0
        test = 0
        while i < len(windows_) - 1:
            current = windows_[i]
            next_ = windows_[i + 1]
            current_score = survey.score_students(current)
            next_score = survey.score_students(next_)
            if current_score >= next_score:
                return current
            i += 1
            if i == len(windows_) - 1:
                i = -1
                test += 1
            if test == 2:
                break

    def _best_match(self, survey: Survey, all_students: List[Student],
                    ones: List[Student]) -> List[Student]:
        """
        Return a list containing the combination of students that has the
        highest score.
        """
        raise NotImplementedError


class Group:
    """
    A group of one or more students

    === Private Attributes ===
    _members: a list of unique students in this group

    === Representation Invariants ===
    No two students in _members have the same id
    """

    _members: List[Student]

    def __init__(self, members: List[Student]) -> None:
        """ Initialize a group with members <members> """
        self._members = members

    def __len__(self) -> int:
        """ Return the number of members in this group """
        return len(self._members)

    def __contains__(self, member: Student) -> bool:
        """
        Return True iff this group contains a member with the same id
        as <member>.
        """
        for one in self._members:
            if one.id == member.id:
                return True
        return False

    def __str__(self) -> str:
        """
        Return a string containing the names of all members in this group
        on a single line.

        You can choose the precise format of this string.
        """
        names = ''
        for member in self._members:
            names = names + str(member) + ' '
        return names

    def get_members(self) -> List[Student]:
        """ Return a list of members in this group. This list should be a
        shallow copy of the self._members attribute.
        """
        members = []
        for member in self._members:
            members.append(member)
        return members


class Grouping:
    """
    A collection of groups

    === Private Attributes ===
    _groups: a list of Groups

    === Representation Invariants ===
    No group in _groups contains zero members
    No student appears in more than one group in _groups
    """

    _groups: List[Group]

    def __init__(self) -> None:
        """ Initialize a Grouping that contains zero groups """
        self._groups = []

    def __len__(self) -> int:
        """ Return the number of groups in this grouping """
        return len(self._groups)

    def __str__(self) -> str:
        """
        Return a multi-line string that includes the names of all of the members
        of all of the groups in <self>. Each line should contain the names
        of members for a single group.

        You can choose the precise format of this string.
        """
        list_of_names = ''
        for group in self._groups:
            for member in group.get_members():
                list_of_names = list_of_names + str(member) + ' '
            list_of_names += '\n'
        return list_of_names

    def add_group(self, group: Group) -> bool:
        """
        Add <group> to this grouping and return True.

        Iff adding <group> to this grouping would violate a representation
        invariant don't add it and return False instead.
        """
        # if there is no member in the group, cannot add
        if len(group) == 0:
            return False

        # if there is a duplicate, do not add
        ids = []
        for fixed_group in self._groups:
            for member in fixed_group.get_members():
                ids.append(member.id)

        for new_member in group.get_members():
            if new_member.id in ids:
                return False
            ids.append(new_member.id)

        self._groups.append(group)
        return True

    def get_groups(self) -> List[Group]:
        """ Return a list of all groups in this grouping.
        This list should be a shallow copy of the self._groups
        attribute.
        """
        groups = []
        for group in self._groups:
            groups.append(group)
        return groups


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={'extra-imports': ['typing',
                                                  'random',
                                                  'survey',
                                                  'course']})
