;; Read this like:  for any major-mode (`nil`), `eval`uate the following form:
;; (if ....  (org-mode))

((nil (eval . (if (string-match ".txt$" (buffer-file-name))(org-mode)))))
