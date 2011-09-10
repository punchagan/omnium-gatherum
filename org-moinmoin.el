;;; org-moinmoin.el --- moinmoin backend for org-export.el
;;
;; Copyright 2010 Bastien Guerry
;;
;; Emacs Lisp Archive Entry
;; Filename: org-moinmoin.el
;; Version: 0.1
;; Author: Puneeth Chaganti <punchagan [at] gmail [dot] com>
;;
;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation; either version 3, or (at your option)
;; any later version.
;;
;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.
;;
;; You should have received a copy of the GNU General Public License
;; along with this program; if not, write to the Free Software
;; Foundation, Inc., 51 Franklin Street, Suite 500, Boston, MA 02110.
;;
;; A portion of this code is based on org-mediawiki.el by Bernt Hansen
;; available at http://lumiere.ens.fr/~guerry/u/org-mediawiki.el.  The
;; Copyright notice from that file is given below.
;; 
;; Copyright 2010 Bastien Guerry
;;
;; Emacs Lisp Archive Entry
;; Filename: org-mediawiki.el
;; Version: 0.3a
;; Author: Bastien <bzg AT altern DOT org>
;; Maintainer: Bastien <bzg AT altern DOT org>
;; Keywords:
;; Description:
;; URL: [Not distributed yet]
;;
;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation; either version 3, or (at your option)
;; any later version.
;;
;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.
;;
;; You should have received a copy of the GNU General Public License
;; along with this program; if not, write to the Free Software
;; Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
;;
;;; Commentary:
;;
;; org-moinmoin.el lets you convert Org files to moinmoin files using
;; the org-export.el experimental engine.
;;
;; Put this file into your load-path and the following into your ~/.emacs:
;;   (require 'org-moinmoin)
;;
;; You also need to fetch Org's git repository and add the EXPERIMENTAL/
;; directory in your load path.
;; 
;; Fetch Org's git repository:
;; 
;; ~$ cd ~/install/git/
;; ~$ git clone git://repo.or.cz/org-mode.git
;;
;; Put this in your .emacs.el:
;; 
;; (add-to-list 'load-path "~/install/git/org-mode/EXPERIMENTAL/")
;;
;; Export Org files to moinmoin: M-x org-mm-export RET
;;
;;; Todo:
;; 
;; - handle radio links
;; - support caption and attributes in tables
;; - better handline of source code and examples
;; - handle inline HTML
;;
;;; Code:

(require 'org-export)

(defvar org-mm-emphasis-alist
  '(("*" "'''%s'''" nil)
    ("/" "''%s''" nil)
    ("_" "__%s__" nil)
    ("+" "--%s--" nil)
    ("=" "`%s`" nil))
  "The list of fontification expressions for moinmoin.")

(defvar org-mm-export-table-table-style "")
(defvar org-mm-export-table-header-style "")
(defvar org-mm-export-table-cell-style "")

(defun org-mm-export ()
  "Export the current buffer to Moinmoin."
  (interactive)
  (org-export-set-backend "mm")
  ;; FIXME see the problem `org-mm-export-footnotes'
  ;; (add-hook 'org-export-preprocess-final-hook 'org-mm-export-footnotes)
  (add-hook 'org-export-preprocess-before-backend-specifics-hook
            'org-mm-export-src-example)
  (org-export-render)
  (remove-hook 'org-export-preprocess-final-hook 'org-mm-export-footnotes)
  (remove-hook 'org-export-preprocess-before-backend-specifics-hook 
               'org-mm-export-src-example))

(defun org-mm-export-header ()
  "Export the header part."
  (let* ((p (org-combine-plists (org-infile-export-plist) 
                                org-export-properties))
	 (title (plist-get p :title))
	 (author (plist-get p :author))
	 (date (plist-get p :date))
         (level (plist-get p :headline-levels)))
    (insert (format "= %s by %s =\n\n" title author))
    (if (plist-get p :table-of-contents)
        (insert (format "<<TableOfContents(%s)>>\n" level)))))

(defun org-mm-export-first-lines (first-lines)
  "Export first lines."
  (insert (org-export-render-content first-lines) "\n")
  (goto-char (point-max)))

(defun org-mm-export-heading (section-properties)
  "Export moinmoin heading"
  (let* ((p section-properties)
	 (h (plist-get p :heading))
	 (s (make-string (1+ (plist-get p :level)) ?=)))
    (insert (format "%s %s %s\n" s h s))))

(defun org-mm-export-quote-verse-center ()
  "Export #+BEGIN_QUOTE/VERSE/CENTER environments."
  (let (rpl e)
    (while (re-search-forward "^[ \t]*ORG-\\([A-Z]+\\)-\\(START\\|END\\).*$" nil t)
      (setq e (if (equal (match-string 2) "END") "/" "")) 
      (setq rpl 
	    (cond ((equal (match-string 1) "BLOCKQUOTE") "blockquote>")
		  ((equal (match-string 1) "VERSE") "pre>")
		  ((equal (match-string 1) "CENTER") "center>")))
      (replace-match (concat "<" e rpl) t))))

(defun org-mm-export-fonts ()
  "Export fontification."
  (while (re-search-forward org-emph-re nil t)
    (let* ((emph (assoc (match-string 3) org-mm-emphasis-alist))
	   (beg (match-beginning 0))
	   (begs (match-string 1))
	   (end (match-end 0))
	   (ends (match-string 5))
	   (rpl (format (cadr emph) (match-string 4))))
      (delete-region beg end)
      (insert begs rpl ends))))

(defun org-mm-export-links ()
  "Replace Org links with moinmoin links."
  ;; FIXME: This function could be more clever, of course.
  (while (re-search-forward org-bracket-link-analytic-regexp nil t)
    (cond ((and (equal (match-string 1) "file:")
		(save-match-data
		  (string-match (org-image-file-name-regexp) (match-string 3))))
	   (replace-match 
	    (concat "{{" (file-name-nondirectory (match-string 3)) "}}")))
	  (t 
	   (replace-match 
	    (concat "[[\\1\\3|" (if (match-string 5) "\\5]]" "]]")))))))

;; FIXME this function should test whether [1] is really a footnote.
;; `org-footnote-normalize' should add properties to the normalized
;; footnotes so that we can recognize them.
(defun org-mm-export-footnotes ()
  "Export footnotes."
  (goto-char (point-min))
  (let (refpos rpl begnote begfullnote endnote)
    (while (re-search-forward "\[[0-9]+\]" nil t)
	(save-excursion
	  (save-match-data
	    (goto-char (point-max))
	    (search-backward (concat (match-string 0) " ") nil t)
	      (setq begfullnote (match-beginning 0))
	      (setq begnote (match-end 0))
	      (goto-char (match-end 0))
	      (re-search-forward "^\[[0-9]+\]\\|\\'" nil t)
	      (setq endnote (match-beginning 0))
	      (setq rpl (replace-regexp-in-string
			 "\n" " " (buffer-substring endnote begnote)))
	      (setq rpl (replace-regexp-in-string "[ \t]+$" "" rpl))
	      (delete-region begfullnote endnote)))
	(replace-match (concat "<ref>" rpl "</ref>")))))

(defun org-mm-export-src-example ()
  "Export #+BEGIN_EXAMPLE and #+BEGIN_SRC."
  (goto-char (point-min))
  (let (start env)
    (while (re-search-forward "^[ \t]*#\\+BEGIN_\\(EXAMPLE\\|SRC\\).*\n" nil t)
      (setq env (match-string 1))
      (replace-match "{{{\n")
      (setq start (point))
      (re-search-forward (concat "^[ \t]*#\\+END_" env ".*\n") nil t)
      (replace-match "}}}\n"))))

(defun org-mm-export-lists ()
  "Export lists"
  (while (re-search-forward org-item-beginning-re nil t)
    (move-beginning-of-line 1)
    (org-list-to-mm (org-list-parse-list t))))

(defun org-list-to-mm (list &optional level)
  "Convert LIST into a moinmoin list.
LIST is a list returned by `org-list-parse-list'.  A second
optional LEVEL argument defines the level at which the parsing
starts.  An optional third argument LEVELUPTYPE tells what type
of list we are in at LEVEL."
  (let ((lvl (or level 1))
	(ltype (cond ((eq (car list) 'unordered) ?*)
		     ((eq (car list) 'ordered) ?#)
                     ((eq (car list) 'descriptive) ?\ ))))
    (dolist (item (cdr list))
      (if (stringp item)
	  (progn
	    (setq item (replace-regexp-in-string "\n[ \t]*" " " item))
	    (insert (make-string lvl ? )
		    (char-to-string ltype) " " item "\n"))
	(org-list-to-mm item (1+ lvl))))))

(defun org-mm-export-tables ()
  "Convert tables in the current buffer to moinmoin tables."
  (while (re-search-forward "^\\([ \t]*\\)|" nil t)
    (org-if-unprotected-at (1- (point))
      (org-table-align)
      (let* ((beg (org-table-begin))
             (end (org-table-end))
             (raw-table (buffer-substring beg end)) lines)
	(setq lines (org-split-string raw-table "\n"))
	(apply 'delete-region (list beg end))
	(when org-export-table-remove-special-lines
	  (setq lines (org-table-clean-before-export lines 'maybe-quoted)))
	(setq lines
	      (mapcar
	       (lambda(elem)
		 (or (and (string-match "[ \t]*|-+" elem) 'hline)
		     (org-split-string (org-trim elem) "|")))
	       lines))
	(insert (orgtbl-to-mm lines nil))))))

(defun orgtbl-to-mm (table params)
  "Convert TABLE into a moinmoin table."
  (let ((params2 (list
		  :tstart (concat "" 
				  org-mm-export-table-table-style)
		  :tend "\n"
		  :lstart "||"
		  :lend "||"
		  :sep "||"
		  :fmt (concat org-mm-export-table-cell-style " %s ")
		  :hfmt (concat org-mm-export-table-cell-style "''' %s '''")
		  :hlsep "||"
		  )))
    (orgtbl-to-generic table (org-combine-plists params2 params))))

;; Various empty function for org-export.el to work:
(defun org-mm-export-footer () "")
(defun org-mm-export-section-beginning (section-properties) "")
(defun org-mm-export-section-end (section-properties) "")
